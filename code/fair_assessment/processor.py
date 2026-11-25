import logging
import os
from logging.handlers import TimedRotatingFileHandler
import queue
import threading
import paho.mqtt.client as mqtt
import json
import sqlite3
import importlib
import traceback

# Database configuration
DB_PATH = os.getenv(
    "DB_PATH", "../service/api_control.db"
)
DB_TIMEOUT = int(os.getenv("DB_TIMEOUT", "30"))

# MQTT configuration
MQTT_HOST = os.getenv("MQTT_HOST", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))

# Logging configuration
LOG_DIR = os.getenv("LOG_DIR", "../../logs")

# Define log file path with date suffix
log_file = os.path.join(LOG_DIR, "processor.log")

# Set up rotating file handler (daily rotation)
handler = TimedRotatingFileHandler(
    log_file,
    when="midnight",     # Rotate at midnight
    interval=1,
    backupCount=7,       # Keep logs for 7 days
    encoding="utf-8"
)

# Set log format
formatter = logging.Formatter(
    "[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
handler.setFormatter(formatter)

# Set up the root logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(handler)

JOB_SCHEDULED = 0
JOB_RUNNING = 1
JOB_COMPLETED = 2
JOB_ERROR = 3

DB_PATH = os.getenv("DB_PATH", "/data/api_control.db")

fifo_queue = queue.Queue(0)

# Create a stop signal for a thread
stop_event = threading.Event()

def load_class(module_path: str, class_name: str):
    module = importlib.import_module(module_path)
    cls = getattr(module, class_name)
    return cls

def get_db():
    conn = sqlite3.connect(
        DB_PATH,
        timeout=DB_TIMEOUT
    )
    conn.execute(f"PRAGMA busy_timeout={DB_TIMEOUT * 1000}")
    return conn

def get_db_algorithm(job_id:str):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT algorithm_id FROM jobs WHERE ticket = ?", (job_id,))
    result = cursor.fetchone()

    conn.close()

    if result:
        return result[0]  # algorithm_id
    else:
        return None  # Ticket not found

def update_job(ticket: str, status: int):
    conn = get_db()

    try:
        conn.execute(
            "UPDATE jobs SET status = ? WHERE ticket = ?",
            (status, ticket)
        )
        conn.commit()
    finally:
        conn.close()

def on_connect(client, userdata, flags, rc):  # The callback for when the client connects to the broker
    logger.info("Connected  to channel job/create")  # Print result of connection attempt
    client.subscribe("job/create")  # Subscribe to the topic “digitest/test1”, receive any messages published on it

def on_message(client, userdata, msg):  # The callback for when a PUBLISH message is received from the server.
    logger.info("Message received-> " + msg.topic + " " + str(msg.payload))  # Print a received msg
    message_json = json.loads(msg.payload)
    logger.info(str(message_json["ticket"])+" ticket added to queue")
    fifo_queue.put(message_json)

def is_url(s: str) -> bool:
    if not isinstance(s, str) or len(s) < 5:
        return False
    return s.startswith("http://") or s.startswith("https://")
    
def run_fairos():
    while 1:
        logger.debug("Waiting for new job")
        next_job = fifo_queue.get()
        logger.info(f"New job: {next_job}")

        update_job(next_job["ticket"],JOB_RUNNING)

        try:
            logger.info(f"Calculating FAIRness of job {next_job}")
            algorithm_id = get_db_algorithm(next_job["ticket"])
            algorithm = load_class('algorithms.'+algorithm_id,algorithm_id)
            logger.info(f"Algorithm {algorithm.get_id()} loaded")
            filename = next_job["file"]
            if is_url(filename):
                logger.info(f"URL to process {filename}")
                algorithm.execute_algorithm_uri(filename, next_job["ticket"])
            else:
                logger.info(f"File to process {filename}")
                algorithm.execute_algorithm(filename, next_job["ticket"])
            '''
            ROFairnessCalculator(ro_path).\
                calculate_fairness(evaluate_ro_metadata,
                            aggregation_mode,
                            output_file_name,
                            generate_diagram)
            logging.info("Updating jobs status")
            update_job(next_job,JOB_COMPLETED)
            logging.info("Job status updated to COMPLETED")
            
            os.system("rm -rf /tmp/"+next_job)
            '''
        except Exception as e:
    
            logger.error("Job status updated to ERROR")
            update_job(next_job["ticket"],JOB_ERROR)

            traceback.print_exc()  # prints directly to stderr
            # or
            print(traceback.format_exc())  # returns traceback as a string

logger.info("Initializing processor")

logger.info("Launching processing thread")
t1= threading.Thread(target=run_fairos)
t1.start()

try:
    client = mqtt.Client()  # Create instance of client with client ID “digi_mqtt_test”
    client.on_connect = on_connect  # Define callback function for successful connection
    client.on_message = on_message  # Define callback function for receipt of a message
    logger.info("Connecting to broker")
    client.connect(MQTT_HOST, MQTT_PORT)
    
    client.loop_forever()  # Start networking daemon
    logger.info("Connecting to broker 3")
except ConnectionRefusedError:
    logger.error("Could not connect: broker not running or wrong port.")
    stop_event.set()

    # Wait for thread to finish
    t1.join()
except OSError as e:
    logger.error(f"OS/network error: {e}")
    # Signal the thread to stop
    stop_event.set()

    # Wait for thread to finish
    t1.join()
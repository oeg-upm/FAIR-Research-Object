#from fairness_calculator import ROFairnessCalculator
import threading
import paho.mqtt.client as mqtt
import os
import json
import sqlite3 as sql
import queue
import traceback
from logging.handlers import TimedRotatingFileHandler
import logging as logging
import subprocess

SCHEDULED = 0
RUNNING = 1
COMPLETED = 2
ERROR = 3

fifo_queue = queue.Queue(0)


def run_fairos():
    while 1:
        logging.debug("Waiting for new job")
        next_job = fifo_queue.get()
        logging.info('Processing job:'+next_job)

        update_job(next_job,RUNNING)
        #os.system("mkdir /tmp/"+next_job+" & unzip  /home/egonzalez/FAIR_assessment_service/pending_jobs/"+next_job+".zip -d /tmp/"+next_job)
        #print("Creating directory: /tmp/"+next_job)
        #print("Moving file "+next_job+".jsonld to ")
        #os.system("mkdir /tmp/"+next_job+" & mv /home/egonzalez/FAIR_assessment_service/pending_jobs/"+next_job+".jsonld /tmp/"+next_job+"/ro-crate-metadata.json")
        message = subprocess.check_output(['mkdir','/tmp/'+next_job])
        logging.debug(message)
        message = subprocess.check_output(['mv','/home/egonzalez/FAIR_assessment_service/pending_jobs/'+next_job+'.jsonld','/tmp/'+next_job+'/ro-crate-metadata.json'])
        logging.debug(message)
        ro_path = "/tmp/"+next_job
        evaluate_ro_metadata = True
        aggregation_mode=0
        output_file_name ="/home/egonzalez/FAIR_assessment_service/completed_jobs/"+next_job+".json"
        generate_diagram = False
        try:
            logging.debug("Calculating FAIRness od job"+str(next_job));
 #           ROFairnessCalculator(ro_path).\
 #               calculate_fairness(evaluate_ro_metadata,
 #                           aggregation_mode,
 #                           output_file_name,
 #                           generate_diagram)
            logging.debug("Updating jobs status")
            update_job(next_job,COMPLETED)
            logging.debug("Job status updated to COMPLETED")
            os.system("rm -rf /tmp/"+next_job)
        except:
            logging.error("Job status updated to ERROR")
            update_job(next_job,ERROR)
            traceback.print_exc()

def update_job (ticket: str, status:int):
    conn = sql.connect("/home/egonzalez/FAIR_assessment_service/Database/enrrichmentDB.db")
    cursor = conn.cursor()
    instruction = f"UPDATE jobs SET ready='{status}' WHERE job_id = '{ticket}'"

    cursor.execute(instruction)
    conn.commit()
    cursor.close()

def on_connect(client, userdata, flags, rc):  # The callback for when the client connects to the broker
    logging.info("Connected with result code {0}".format(str(rc)))  # Print result of connection attempt
    client.subscribe("job/create")  # Subscribe to the topic “digitest/test1”, receive any messages published on it


def on_message(client, userdata, msg):  # The callback for when a PUBLISH message is received from the server.
    logging.debug("Message received-> " + msg.topic + " " + str(msg.payload))  # Print a received msg
    message_json = json.loads(msg.payload)
    logging.debug(str(message_json["ticket"])+" ticket added to queue")
    fifo_queue.put(message_json["ticket"])


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

logname = "log/fairos_evaluator.log"
handler = TimedRotatingFileHandler(logname, when="midnight", interval=1)
handler.suffix = "%Y%m%d"
logger.addHandler(handler)


t1= threading.Thread(target=run_fairos)
t1.start()

t2= threading.Thread(target=run_fairos)
t2.start()

t3= threading.Thread(target=run_fairos)
t3.start()

client = mqtt.Client("worker")  # Create instance of client with client ID “digi_mqtt_test”
client.on_connect = on_connect  # Define callback function for successful connection
client.on_message = on_message  # Define callback function for receipt of a message
client.connect('localhost', 1883)

client.loop_forever()  # Start networking daemon


#ro_path = "/tmp/ro_assessment/589b9da4-10f4-4024-8df9-f2cdd284c466/"
#evaluate_ro_metadata = True
#aggregation_mode=0
#output_file_name = "/home/egonzalez/FAIR_assessment_service/completed_jobs/prueba.json"
#generate_diagram=False

#ROFairnessCalculator(ro_path).\
#        calculate_fairness(evaluate_ro_metadata,
#                           aggregation_mode,
#                           output_file_name,
#                           generate_diagram)


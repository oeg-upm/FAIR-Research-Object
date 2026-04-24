from fastapi import FastAPI, Request, HTTPException, Depends, Body, UploadFile, File, status, Form
from fastapi.responses import JSONResponse
from pathlib import Path
from fastapi.responses import FileResponse
from datetime import datetime, UTC
import sqlite3
import random
import os
import logging
from logging.handlers import TimedRotatingFileHandler
from config import settings
import paho.mqtt.client as mqtt
from contextlib import asynccontextmanager
from pathlib import Path
from rdflib import Graph, URIRef, RDF
import json
from typing import Optional

# Create logs directory if it doesn't exist
LOG_DIR = "../../logs"
os.makedirs(LOG_DIR, exist_ok=True)

JOB_SCHEDULED = 0
JOB_RUNNING = 1
JOB_COMPLETED = 2
JOB_ERROR = 3

# Define log file path with date suffix
log_file = os.path.join(LOG_DIR, "service.log")

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

DB_PATH = "api_control.db"

def extract_metric_uris(metrics_root: Path) -> list[str]:
    metric_uris = []
    METRIC_TYPE = URIRef("http://www.w3.org/ns/dqv#Metric")

    for ttl_file in metrics_root.rglob("*.ttl"):
        g = Graph()
        try:
            g.parse(ttl_file, format="turtle")
        except Exception as e:
            print(f"Skipping {ttl_file} (parse error): {e}")
            continue

        for s in g.subjects(RDF.type, METRIC_TYPE):
            if isinstance(s, URIRef):
                metric_uris.append(str(s))

    return metric_uris

def extract_test_uris(tests_root: Path) -> list[str]:
    test_uris = []
    TEST_TYPE = URIRef("https://w3id.org/ftr#Test")

    for ttl_file in tests_root.rglob("*.ttl"):
        g = Graph()
        try:
            g.parse(ttl_file, format="turtle")
        except Exception as e:
            print(f"Skipping {ttl_file} (parse error): {e}")
            continue

        for s in g.subjects(RDF.type, TEST_TYPE):
            if isinstance(s, URIRef):
                test_uris.append(str(s))

    return test_uris

def extract_benchmark_uris(benchmarks_root: Path) -> list[str]:
    benchmark_uris = []
    TEST_TYPE = URIRef("https://w3id.org/ftr#Benchmark")

    for ttl_file in benchmarks_root.rglob("*.ttl"):
        g = Graph()
        try:
            g.parse(ttl_file, format="turtle")
        except Exception as e:
            print(f"Skipping {ttl_file} (parse error): {e}")
            continue

        for s in g.subjects(RDF.type, TEST_TYPE):
            if isinstance(s, URIRef):
                benchmark_uris.append(str(s))

    return benchmark_uris

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting service")

    logger.info("Loading metrics")
    metric_uris = extract_metric_uris(settings.METRICS_DIRECTORY)
    app.state.metric_uris = metric_uris
    logger.info(f" {len(metric_uris)} metrics loaded")

    logger.info("Loading tests")
    test_uris = extract_test_uris(settings.TESTS_DIRECTORY)
    app.state.test_uris = test_uris
    logger.info(f" {len(test_uris)} tests loaded")

    logger.info("Loading benchmarks")
    benchmark_uris = extract_benchmark_uris(settings.BENCHMARKS_DIRECTORY)
    app.state.benchmark_uris = benchmark_uris
    logger.info(f" {len(benchmark_uris)} benchmarks loaded")

    yield

app = FastAPI(lifespan=lifespan)

@app.get("/")
def read_root():
    return {"message": "Welcome to FAIROs, a service to assess Research Objects."}

@app.get("/metrics")
def get_tests():
    return app.state.metric_uris

@app.get("/tests")
def get_tests():
    return app.state.test_uris

@app.get("/benchmarks")
def get_benchmarks():
    return app.state.benchmark_uris

def get_db():
    return sqlite3.connect(DB_PATH)

def get_client_ip(request: Request):
    return request.client.host  # You can adjust for proxies if needed

def check_access(request: Request):
    conn = get_db()
    cursor = conn.cursor()
    token = request.headers.get("Authorization")

    # Token-based access (no limit)
    if token:
        cursor.execute("SELECT token FROM tokens WHERE token = ?", (token,))
        if cursor.fetchone():
            conn.close
            return  "private"
        else:
            conn.close()
            raise HTTPException(status_code=403, detail="Invalid token")

    # IP-based access (rate limited)
    ip = get_client_ip(request)
    today = datetime.now().date().isoformat()
    cursor.execute("SELECT count FROM ip_requests WHERE ip = ? AND date = ?", (ip, today))
    row = cursor.fetchone()

    if row:
        if row[0] >= 100:
            raise HTTPException(status_code=429, detail="Daily request limit reached for this IP")
        cursor.execute("UPDATE ip_requests SET count = count + 1 WHERE ip = ? AND date = ?", (ip, today))
    else:
        cursor.execute("INSERT INTO ip_requests (ip, date, count) VALUES (?, ?, ?)", (ip, today, 1))

    conn.commit()
    conn.close()
    return "public"
    

@app.post("/assess/algorithm/{algorithm_id}")
def execute_algorithm(
    algorithm_id: str,
    file: Optional[UploadFile] = File(None),
    resource_id: Optional[str] = Form(None),
    storage_mode: str = Depends(check_access),  # This ensures check_access runs
    request: Request = None,  # Optional, only if you need request inside
):
    timestamp = datetime.now(UTC).strftime("%Y%m%d%H%M%S")
    random_suffix = random.randint(1000, 9999)
    ticket_id = f"{timestamp}-{random_suffix}"
    logger.info(f"New request arrived to execute algorithm '{algorithm_id}'. New ticket generated: {ticket_id}")
    
    if file is None and not resource_id:
        raise HTTPException(status_code=400, detail="Either a file or a resource_identifier must be provided.")

    if file and not resource_id:
        filename = f"{ticket_id}_{file.filename}"
        filename_without_ext = Path(filename).stem
        
            # Determine directory based on access type
        target_dir = Path(settings.FILE_STORAGE_DIR if storage_mode == "private" else settings.NO_TOKEN_DIRECTORY / filename_without_ext)
        target_dir.mkdir(parents=True, exist_ok=True)  # Ensure it exists

        # Save the uploaded file to the FILE_STORAGE_DIR

        save_path = target_dir / "ro-crate-metadata.json"

        with open(save_path, "wb") as f:
            f.write(file.file.read())

        logger.info(f"Metadata file stored in {save_path}")

        logger.info(
            f"File '{file.filename}' uploaded from IP {request.client.host} → ticket {ticket_id}"
        )

        #Creating job in database
        logger.info(f"Creating job to process a file with ticket {ticket_id}")
        conn = get_db()
        cursor = conn.cursor()                
        instruction = f"INSERT INTO jobs VALUES ('{ticket_id}','{file.filename}',{JOB_SCHEDULED},'{algorithm_id}')"
        cursor.execute(instruction)
        conn.commit()
        conn.close()
        logger.info(f"Job created to process ticket {ticket_id}")

        #Publish job in mqtt server
        #mqtt_message={"ticket":ticket_id, "file":file.filename, "algorithm":algorithm_id}
        mqtt_message={"ticket":ticket_id, "file":str(target_dir), "algorithm":algorithm_id}
        logger.info(f"Sending message to broker: {str(mqtt_message)}")
        client = mqtt.Client()
        client.connect(settings.MQTT_HOST,settings.MQTT_PORT) 
        client.publish("job/create",json.dumps(mqtt_message))
        client.disconnect()
        client.loop_stop()
        logger.info("Message published")

    if not file and resource_id:
        #Creating job in database
        logger.info(f"Creating job to process a url with ticket {ticket_id}")
        conn = get_db()
        cursor = conn.cursor()                
        instruction = f"INSERT INTO jobs VALUES ('{ticket_id}','{resource_id}',{JOB_SCHEDULED},'{algorithm_id}')"
        cursor.execute(instruction)
        conn.commit()
        conn.close()
        logger.info(f"Job created to process ticket {ticket_id}")

        #Publish job in mqtt server
        #mqtt_message={"ticket":ticket_id, "file":file.filename, "algorithm":algorithm_id}
        mqtt_message={"ticket":ticket_id, "file":str(resource_id), "algorithm":algorithm_id}
        logger.info(f"Sending message to broker: {str(mqtt_message)}")
        client = mqtt.Client()
        client.connect(settings.MQTT_HOST,settings.MQTT_PORT) 
        client.publish("job/create",json.dumps(mqtt_message))
        client.disconnect()
        client.loop_stop()
        logger.info("Message published")

    # Build absolute URL to the polling endpoint
    location = str(request.url_for("get_score", ticket_id=ticket_id))

    # Return 202 + Location header
    return JSONResponse(
        status_code=status.HTTP_202_ACCEPTED,
        content={"ticket_id": ticket_id},
        headers={"Location": location},
    )
    
'''  return {
        "ticket_id": ticket_id
    }'''

@app.get("/assess/score/{ticket_id}")
def get_score(ticket_id: str):
    filename = settings.SCORE_DIRECTORY / f"score-{ticket_id}.jsonld"
    #logger(f"Requesting score {ticket_id}")

    path = Path(filename)
    if not path.is_file():
        raise HTTPException(status_code=404, detail="Not found")
    # filename -> sets Content-Disposition for download; omit it to serve inline
    return FileResponse(path, media_type="application/json", filename=ticket_id+".json")
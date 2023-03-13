from fairness_calculator import ROFairnessCalculator
import threading
import paho.mqtt.client as mqtt
import os
import json
import sqlite3 as sql
import queue
import traceback

SCHEDULED = 0
RUNNING = 1
COMPLETED = 2
ERROR = 3

fifo_queue = queue.Queue(10)


def run_fairos():
    while 1:
        next_job = fifo_queue.get()
        print('Processing job:'+next_job)

        update_job(next_job,RUNNING)
        #os.system("mkdir /tmp/"+next_job+" & unzip  /home/egonzalez/FAIR_assessment_service/pending_jobs/"+next_job+".zip -d /tmp/"+next_job)
        #print("Creating directory: /tmp/"+next_job)
        #print("Moving file "+next_job+".jsonld to ")
        os.system("mkdir /tmp/"+next_job+" & mv /home/egonzalez/FAIR_assessment_service/pending_jobs/"+next_job+".jsonld /tmp/"+next_job+"/ro-crate-metadata.json")
        ro_path = "/tmp/"+next_job
        evaluate_ro_metadata = True
        aggregation_mode=0
        output_file_name ="/home/egonzalez/FAIR_assessment_service/completed_jobs/"+next_job+".json"
        generate_diagram = False
        try:
            ROFairnessCalculator(ro_path).\
                calculate_fairness(evaluate_ro_metadata,
                            aggregation_mode,
                            output_file_name,
                            generate_diagram)
            update_job(next_job,COMPLETED)
        except:
            update_job(next_job,ERROR)
            traceback.print_exc()
        os.system("rm -rf /tmp/"+next_job)

def update_job (ticket: str, status:int):
    conn = sql.connect("/home/egonzalez/FAIR_assessment_service/Database/enrrichmentDB.db")
    cursor = conn.cursor()
    instruction = f"UPDATE jobs SET ready='{status}' WHERE job_id = '{ticket}'"

    cursor.execute(instruction)
    conn.commit()
    cursor.close()

def on_connect(client, userdata, flags, rc):  # The callback for when the client connects to the broker
    print("Connected with result code {0}".format(str(rc)))  # Print result of connection attempt
    client.subscribe("job/create")  # Subscribe to the topic “digitest/test1”, receive any messages published on it


def on_message(client, userdata, msg):  # The callback for when a PUBLISH message is received from the server.
    print("Message received-> " + msg.topic + " " + str(msg.payload))  # Print a received msg
    message_json = json.loads(msg.payload)
    fifo_queue.put(message_json["ticket"])


t1= threading.Thread(target=run_fairos)
t1.start()

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


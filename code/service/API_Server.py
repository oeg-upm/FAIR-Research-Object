from flask import Flask, request, jsonify, send_file
from flask_restful import Api, Resource
import os, uuid, jwt, json, time, datetime as dt, sqlite3 as sql
from werkzeug.security import generate_password_hash, check_password_hash
from logging.handlers import TimedRotatingFileHandler
import logging as logging
import paho.mqtt.client as mqtt
import json


mqttBroker = "localhost"

UPLOAD_FOLDER = '../pending_jobs'
DOWNLOAD_FOLDER = '../completed_jobs'
SECRET_KEY = 'MY_PASSWORD'
ALLOWED_EXTENSIONS = {'json', 'jsonld','zip'}

client = mqtt.Client()
client.connect(mqttBroker,1883) 

# Start the flask API app
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER
app.config['SECRET_KEY'] = SECRET_KEY
api = Api(app)

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

logname = "../log/fairos.log"
handler = TimedRotatingFileHandler(logname, when="midnight", interval=1)
handler.suffix = "%Y%m%d"
logger.addHandler(handler)
    

def allowed_file(filename):
    	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
 
def token_authentication (token):
    try:
        data = jwt.decode(token, app.config['SECRET_KEY'], "HS256")
    except:
        return False    
    id = data.get("id")
    
    conn = sql.connect("../Database/enrrichmentDB.db")
    cursor = conn.cursor()
   
    instruction = f"SELECT username FROM users WHERE id = '{id}'"
    result = cursor.execute(instruction).fetchone()
    if result:
        return result[0]
    return False

def get_status (ticket: str):
    conn = sql.connect("./Database/enrrichmentDB.db")
    cursor = conn.cursor()
    instruction = f"SELECT * FROM jobs WHERE job_id = '{ticket}'"
    
    result = cursor.execute(instruction).fetchone()

    
    if not result:
        return (-1)
    else:
        return (result[3])
    
   

class Jobs (Resource):
    def post(self):
        logging.debug("Job creation request:"+str(self))
        #token = json.loads(request.form.to_dict(flat=False).get('token')[0]).get("token")
        token = request.headers.get('Authorization')
        conn = sql.connect("./Database/enrrichmentDB.db")
        logging.debug(token) 
        user = token_authentication(token)
        logging.debug("user identified:"+str(user))
        if user:
            if 'file' not in request.files:
                message = 'No file part in the request. Please make sure to upload the json/jsonld file.'
                resp = jsonify({'message' : message})
                resp.status_code = 400
                
                logging.error("No file part in the request")

                return resp
            
            file = request.files['file']
            
            if file.filename == '':
                message = 'No file selected for uploading. Please make sure to upload the json/jsonld file.'
                
                resp = jsonify({'message' : message})
                resp.status_code = 400
                
                logging.error("No file selected for uploading.")

                return resp

            if file and allowed_file(file.filename):
                filename = str(uuid.uuid4())+'.'+file.filename.rsplit('.', 1)[1].lower()
                if not os.path.exists(app.config['UPLOAD_FOLDER']):
                    os.makedirs(app.config['UPLOAD_FOLDER'])

                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                ticket = filename.rsplit('.', 1)[0].lower()
                
                if not os.path.exists("Database"):
                    os.makedirs("Database")
                conn = sql.connect("./Database/enrrichmentDB.db")
                cursor = conn.cursor()                
                instruction = f"INSERT INTO jobs VALUES ('{ticket}','{file.filename}','{token}',FALSE)"
                cursor.execute(instruction)
                conn.commit()
                conn.close
                message = 'File successfully uploaded. Please recover your ticket: '+ ticket
                resp = jsonify({'message' : message, 'ticket' : ticket})
                resp.status_code = 201
                
                logging.debug("File uploaded with ticket"+str(ticket))

                mqtt_message={"ticket":ticket, "file":file.filename}
                logging.debug("Sending message to broker:"+str(mqtt_message))
                client.connect(mqttBroker,1883)
                client.publish("job/create",json.dumps(mqtt_message))

                return resp

            else:
                message = 'Please make sure to upload a valid file type. Allowed file types are json and jsonld'
                resp = jsonify({'message' : message})
                resp.status_code = 400
                
                logging.error("Please make sure to upload a valid file type.")

                return resp
        else:
            message = 'You are not allowed to perform this request. Please make sure that you are logged in to the service.'
            resp = jsonify({'message' : message})
            resp.status_code = 400
            
            logging.error("You are not allowed to perform this request.");

            return resp

    def get(sel, job_id):
       
        logging.debug("Job status requested for id:"+str(job_id))

        status = get_status(job_id)
        if status == -1:
            resp.status_code = 404
            logging.error("Job identifier "+str(job_id)+" not present in the database")

            return resp                
                
        else:
            if status == 0:
                message = 'SCHEDULED'
                resp = jsonify({'status' : message})
            elif status == 1:
                message = 'RUNNING'
                resp = jsonify({'status' : message})
            elif status == 2:
                message = 'COMPLETED'
                resp = jsonify({'status' : message})
            elif status == 3:
                message = 'ERROR'
                resp = jsonify({'status' : message, 'msg': 'Problem to load JSON-LD file'})

            resp.status_code = 200
            logging.debug("Job "+str(job_id)+" with status "+message)

            return resp

class login(Resource):
    def post(self):
        if 'username' not in request.json or 'userpassword' not in request.json:
            message = 'Please make sure to send a valid request. Your request is missing a username and/or a password'
            resp = jsonify ({'message' : message})
            resp.status_code = 401
            
            logging.error("Missing username or password")

            return resp

        entry_dict = request.json
        conn = sql.connect("./Database/enrrichmentDB.db")
        cursor = conn.cursor()
        username = entry_dict.get("username")
        
        
        instruction = f"SELECT * FROM users WHERE username = '{username}'"
        result = cursor.execute (instruction)
        for user in result.fetchall():
            if check_password_hash(user[2],entry_dict.get("userpassword")):
                token = jwt.encode({'id':user[0]}, SECRET_KEY, "HS256")
                
                user = user [1]
                message = 'Logged in successfully. Please recover your token'
                resp = jsonify ({'message':message, 'token':token})
                resp.status_code = 200

                logging.debug("Logged in successfully")

                return resp
            else:
                message = 'Login request declined! Please make sure to send a valid username and password'
                resp = jsonify ({'message' : message})
                resp.status_code = 401
                
                logging.error("Wrong combination username/password")

                return resp
class assessment (Resource):
    def get(self,assessment_id):
        filename = app.config['DOWNLOAD_FOLDER'] + '/' +assessment_id+'.json'
        logging.debug("Downloading file:"+filename)
        if os.path.exists(filename):
            resp = send_file(filename, attachment_filename=assessment_id+'.json')
            resp.status_code = 200
        else:
            message = 'File not exist'
            resp = jsonify ({'message':message})
            resp.status_code = 404
        return resp

                

'''
def login (entry_dict: dict):
  conn = sql.connect("Database/enrrichmentDB.db")
  cursor = conn.cursor()
  username = entry_dict.get("username")
  userpassword = generate_password_hash(entry_dict.get("userpassword"))
  instruction = f"SELECT 1 FROM users WHERE username = '{username}' AND userpassword = '{userpassword}'"
  result = cursor.execute (instruction)
  conn.commit()
  conn.close()
  if result:
    CURRENT_USER = result
    token = jwt.encode({'id':result.get('id')}, SECRET_KEY)
    return token
  else:
    return null
    '''    




api.add_resource(Jobs,"/api/jobs/","/api/jobs/<job_id>")
api.add_resource(login,"/api/login/")
api.add_resource(assessment, "/api/assessment/<assessment_id>")

# Execution

if __name__ == "__main__":
    #app.run(debug=True)
    app.run(debug=True,host="0.0.0.0",port=5000)

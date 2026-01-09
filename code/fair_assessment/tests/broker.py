import paho.mqtt.client as mqtt
import logging
import json

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MQTT configuration
MQTT_BROKER = "localhost"   # Change to broker IP or hostname
MQTT_PORT = 1883
TOPIC = "job/create"

# Callback when the client connects to the broker
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logger.info("✅ Connected to MQTT broker.")
        client.subscribe(TOPIC)
        logger.info(f"📡 Subscribed to topic: {TOPIC}")
    else:
        logger.error(f"❌ Failed to connect, return code {rc}")

# Callback when a message is received
def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode('utf-8')
        data = json.loads(payload)  # Assuming JSON payload
        logger.info(f"📨 Received message: {data}")
    except Exception as e:
        logger.error(f"Error parsing message: {e}")

# Create MQTT client and assign callbacks
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

try:
    # Connect to the MQTT broker
    client.connect(MQTT_BROKER, MQTT_PORT, 60)

    # Start listening for messages
    client.loop_forever()

except Exception as e:
    logger.error(f"🚨 Could not connect or listen to broker: {e}")

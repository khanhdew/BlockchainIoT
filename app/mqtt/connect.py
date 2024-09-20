import json
import logging
import random
import time

from paho.mqtt import client as mqtt_client

from app.wallet_service.create_transaction import create_transaction
from app.hashing_service.encrypt import EncryptModel
from app.database.connector import Connector


broker = 'localhost'
port = 1883
topic = "v1/devices/me/telemetry"
# Generate a Client ID with the subscribe prefix.
client_id = f'python-mqtt-{random.randint(0, 1000)}'
last_time = time.time()
datapoint = []
ecrypt = EncryptModel()
conn = Connector()
def connect_mqtt() -> mqtt_client:
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client()
    client.on_connect = on_connect
    client.connect(broker, port)
    return client


def subscribe(client: mqtt_client):
    def on_message(client, userdata, msg):
        global last_time

        try:
            recv_message = msg.payload.decode()
            print(recv_message)
            temp = json.loads(recv_message)
            datapoint.append({
                "temp": int(temp['device']['sensor']['dht']['temp']),
                "humid": int(temp['device']['sensor']['dht']['humid']),
                "soil": int(temp['device']['sensor']['soil']),
                "timestamp": int(time.time())
            })

            # each 5 minutes send data to blockchain
            if time.time() - last_time >= 300:
                data_to_encrypt = json.dumps(datapoint)
                sensor_data = {
                    674: ecrypt.encrypt(data_to_encrypt)
                }
                last_time = time.time()
                tx_log = create_transaction(sensor_data)
                print(tx_log)
                cursor = conn.execute(f"select id from \"hash_key\" where hash = '{ecrypt.key}'")
                ecrypt_key_id = None
                for row in cursor:
                    ecrypt_key_id= row[0]
                conn.execute(f"INSERT INTO \"transaction\" (hash, time, hash_key) VALUES ('{tx_log}', {time.time()}, {ecrypt_key_id})")
                conn.commit()
                datapoint.clear()
                logging.info("Sent data to blockchain")
        except Exception as e:
            logging.error(e)

    client.subscribe(topic)
    client.on_message = on_message


def run():
    client = connect_mqtt()
    subscribe(client)
    client.loop_start()

from paho import mqtt
from db import get_db_connection

mqttc = mqtt.Client()
mqttc.connect("192.168.0.15", 1883, 60)
mqttc.loop_start()


def control_mqtt(id, action):
    conn = get_db_connection()
    device = conn.execute("select * from device where id = ? ",
                          (id,)).fetchall()

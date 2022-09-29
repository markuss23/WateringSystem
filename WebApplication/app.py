import paho.mqtt.client as mqtt
import sqlite3

from _testcapi import awaitType
from flask import Flask, render_template, request

app = Flask(__name__)
"""""
mqttc = mqtt.Client()
mqttc.connect("192.168.0.15", 1883, 60)
mqttc.loop_start()
"""
"""
je potřeba dodělat CRUD funkce,

"""


def get_db_connection():
    ## dodělat ošetření
    conn = sqlite3.connect('db.sqlite')
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/")
def main():
    template_data = {
        'scenes': False,
    }
    try:
        conn = get_db_connection()
        scenes = conn.execute("select * from scene").fetchall()
        conn.close()
        template_data['scenes'] = scenes
    except:
        pass

    return render_template('index.html', **template_data)


@app.route("/<scene>/")
def scene(scene):
    template_data = {
        'datas': False,
        'label': scene
    }
    try:
        conn = get_db_connection()
        datas = conn.execute(
            "select d.label, d.device_topic, d.is_active, d.identifier FROM device d JOIN scene_device sd ON d.id = sd.device_id JOIN scene s ON s.id = sd.scene_id WHERE s.scene_topic = ?",
            (scene + "/",)).fetchall()
        template_data['datas'] = datas
    except:
        pass

    return render_template('scene.html', **template_data)


@app.route("/<scene>/<device>/")
def device(scene, device):
    template_data = {
        'datas': False,
        'label': device
    }
    try:
        conn = get_db_connection()
        datas = conn.execute("select * from device as d where d.device_topic = ?",
                             (device + "/", )).fetchall()
        template_data['datas'] = datas
    except:
        pass
    return render_template('device.html', **template_data)


@app.route("/<scene>/<device>/<action>")
def action(scene, device, action):
    print(type(action))
    conn = get_db_connection()
    try:
        rest_topic = conn.execute("select identifier from device where device.device_topic = ?",
                                  (device + "/",)).fetchall()
        end_topic = ""
        for topic in rest_topic:
            end_topic = ' '.join(topic)
    except:
        pass
    try:
        """""
        if action == "1":
            mqttc.publish(scene+"/"+device+"/"+end_topic + "command", "on")
        if action == "0":
            mqttc.publish(scene+"/"+device+"/"+end_topic + "command", "off")
        """
        return scene + "/" + device + "/" + end_topic + "command"

    except:
        pass


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

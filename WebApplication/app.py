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
                             (device + "/",)).fetchall()
        template_data['datas'] = datas
    except:
        pass
    return render_template('device.html', **template_data)


@app.route("/<scene>/edit/", methods=('GET', 'POST'))
def editScene(scene):
    conn = get_db_connection()
    template_data = {
        'datas': False,
        'label': scene
    }

    try:
        if request.method == 'POST':
            label = request.form['label']
            scene_topic = request.form['scene_topic']
            is_active = request.form.get('is_active')
            if  is_active is None:
                is_active = 0
            else:
                is_active = 1
            try:
                conn.execute("UPDATE scene SET label = ?, scene_topic = ?, is_active = ? WHERE scene.scene_topic = ?",
                             (label, scene_topic, is_active, scene+"/"))
                conn.commit()
            except:
                return "chyba při aktualizaci"
    except:
        pass

    try:
        datas = conn.execute("select * from scene as s where s.scene_topic = ?",
                             (scene + "/",)).fetchall()
        template_data['datas'] = datas
    except:
        pass

    return render_template('views/scene/sceneEdit.html', **template_data)


@app.route("/<scene>/<device>/<action>")
def action(scene, device, action):
    conn = get_db_connection()
    try:
        command = conn.execute("select identifier, label from device where device.device_topic = ?",
                               (device + "/",)).fetchall()
        for split in command:
            help = (' '.join(split)).split(" ")

        command = conn.execute(
            "select label from type where type.id = (select device.type_id from device where device.label = ?)",
            (help[1],)).fetchall()
        for split in command:
            number = (' '.join(split)).split(" ")

    except:
        print("error")
        pass

    try:
        """""
        if action == "1":
            mqttc.publish(scene+"/"+device+"/"+end_topic + "command", "on")
        if action == "0":
            mqttc.publish(scene+"/"+device+"/"+end_topic + "command", "off")
        """
        return scene + "/" + device + "/" + number[0] + help[0] + "command"

    except:
        pass


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

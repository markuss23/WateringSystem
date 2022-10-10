import views

import paho.mqtt.client as mqtt
import sqlite3

from _testcapi import awaitType
from flask import Flask, render_template, request, flash, redirect

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


@app.route("/add/")
def add():
    return "nabídka přidání věcí"


@app.route("/types/add/", methods=('POST', 'GET'))
def add_typ():
    try:
        if request.method == 'POST':
            label = request.form['label']
            typ = request.form['typ']
            jednotka = request.form['jednotka']
            minimum = request.form['min']
            maximum = request.form['max']
            interval = request.form['interval']
            type_topic = request.form['type_topic']
            is_active = request.form.get('is_active')

            conn = get_db_connection()
            if is_active is None:
                is_active = 0
            else:
                is_active = 1
            if type_topic[-1] != "/":
                type_topic = type_topic + "/"
            error = None

            if not label:
                error = 'Název scény chybí'
            if not typ:
                error = 'Chybí typ'
            if not type_topic:
                error = 'Adresa chybí'

            if error is None:
                try:
                    conn.execute("INSERT INTO type VALUES (NULL,?,?,?,?,?,?,?,?)",
                                 (label, typ, jednotka, minimum, maximum, interval, type_topic, is_active))
                    conn.commit()
                except conn.IntegrityError:
                    error = f" Tato adresa již existuje "
                else:
                    return redirect('/')
            flash(error)
    except:
        pass

    return render_template('type/typeAdd.html')


@app.route("/scenes/add/", methods=('POST', 'GET'))
def add_scene():
    try:
        if request.method == 'POST':
            label = request.form['label']
            scene_topic = request.form['scene_topic']
            is_active = request.form.get('is_active')
            conn = get_db_connection()
            if is_active is None:
                is_active = 0
            else:
                is_active = 1
            if scene_topic[-1] != "/":
                scene_topic = scene_topic + "/"
            error = None

            if not label:
                error = 'Název scény chybí'
            if not scene_topic:
                error = 'Adresa chybí'

            if error is None:
                try:
                    conn.execute("INSERT INTO scene VALUES (NULL,?,?,?)",
                                 (label, scene_topic, is_active))
                    conn.commit()
                except conn.IntegrityError:
                    error = f" Tato adresa již existuje "
                else:
                    return redirect('/')
            flash(error)
    except:
        pass

    return render_template('scene/sceneAdd.html')


@app.route("/scenes/")
def scenes():
    template_data = {
        'scenes': False,
        'label': 'Výpis všech scén'
    }
    try:
        conn = get_db_connection()
        scenes = conn.execute("select * from scene").fetchall()
        conn.close()
        template_data['scenes'] = scenes
    except:
        pass
    return render_template('scene/sceneList.html', **template_data)


@app.route("/scenes/<int:id>/")
def scene(id):
    template_data = {
        'scenes': False,
        'devices': False,
    }
    try:
        conn = get_db_connection()
        scenes = conn.execute(
            "select * from scene where scene.id = ?",
            (id,)).fetchall()

        devices = conn.execute(
            "select d.label, d.device_topic, d.is_active, d.pin FROM device d JOIN scene_device sd ON d.id = sd.device_id JOIN scene s ON s.id = sd.scene_id WHERE s.id=?;",
            (id,)).fetchall()

        template_data['scenes'] = scenes
        template_data['devices'] = devices

    except:
        pass

    return render_template('scene/sceneDetail.html', **template_data)


@app.route("/scenes/<int:id>/edit/", methods=('GET', 'POST'))
def edit_scene(id):
    conn = get_db_connection()
    template_data = {
        'datas': False,
    }

    try:
        if request.method == 'POST':
            label = request.form['label']
            scene_topic = request.form['scene_topic']
            is_active = request.form.get('is_active')
            if is_active is None:
                is_active = 0
            else:
                is_active = 1
            if scene_topic[-1] != "/":
                scene_topic = scene_topic + "/"
            error = None

            if not label:
                error = 'Název scény chybí'
            if not scene_topic:
                error = 'Adresa chybí'
            if error is None:
                try:
                    conn.execute(
                        "UPDATE scene SET label = ?, scene_topic = ?, is_active = ? WHERE scene.id = ?",
                        (label, scene_topic, is_active, id))
                    conn.commit()
                except error:
                    error = "chyba při zapsání do Databáze"
                else:
                    redirect('/')
            flash(error)
    except:
        pass

    try:
        datas = conn.execute("select * from scene as s where s.id = ?",
                             (id,)).fetchall()
        template_data['datas'] = datas
    except:
        pass

    return render_template('scene/sceneEdit.html', **template_data)


# -----------------------------------


@app.route("/devices/add/", methods=('POST', 'GET'))
def add_device():
    template_data = {
        'types': False,
    }
    conn = get_db_connection()

    types = conn.execute("select * from type")
    template_data['types'] = types

    try:
        if request.method == 'POST':
            label = request.form['label']
            device_topic = request.form['device_topic']
            is_active = request.form.get('is_active')
            select = request.form.get('types')
            pin = request.form['pin']

            if is_active is None:
                is_active = 0
            else:
                is_active = 1
            if device_topic[-1] != "/":
                device_topic = device_topic + "/"
            error = None

            if not label:
                error = 'Název scény chybí'
            if not device_topic:
                error = 'Adresa chybí'
            if not pin:
                error = 'Pin chybí'

            if error is None:
                try:
                    conn.execute("INSERT INTO device VALUES (NULL,?,?,?,?,?)",
                                 (select, label, device_topic, is_active, pin + '/'))
                    conn.commit()
                except conn.IntegrityError:
                    error = f" Tato adresa již existuje "
                else:
                    return redirect('/')
            flash(error)
    except:
        pass

    return render_template('device/deviceAdd.html', **template_data)


@app.route("/devices/")
def devices():
    template_data = {
        'devices': False,
        'label': 'Výpis všech zařízení'
    }
    try:
        conn = get_db_connection()
        devices = conn.execute("select * from device").fetchall()
        conn.close()
        template_data['devices'] = devices
    except:
        pass
    return render_template('device/deviceList.html', **template_data)


@app.route("/devices/<int:id>/")
def device(id):
    template_data = {
        'devices': False,
        'scenes': False,
    }
    try:
        conn = get_db_connection()
        devices = conn.execute(
            "select * from device where device.id = ?",
            (id,)).fetchall()

        scenes = conn.execute(
            "select s.id, s.label, s.scene_topic, s.is_active from scene s join scene_device sd on s.id = sd.scene_id join device d on d.id = sd.device_id where d.id=?;",
            (id,)).fetchall()

        template_data['devices'] = devices
        template_data['scenes'] = scenes
    except:
        pass

    return render_template('device/deviceDetail.html', **template_data)


@app.route("/<scene>/<device>/<action>")
def action(scene, device, action):
    conn = get_db_connection()
    try:
        command = conn.execute("select pin, label from device where device.device_topic = ?",
                               (device + "/",)).fetchall()
        for split in command:
            help = (' '.join(split)).split(" ")

        command = conn.execute(
            "select type_topic from type where type.id = (select device.type_id from device where device.label = ?)",
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


#app.add_url_rule('/asd/<int:id>/', view_func=views.test)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

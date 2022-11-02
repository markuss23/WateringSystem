import os

from views import auth

import sqlite3

from flask import Flask, render_template, request, flash, redirect, session

app = Flask(__name__)
app.secret_key = "super secret key"


@app.before_request
def load_logged_in_user():
    auth.load_logged_in_user()


@app.errorhandler(404)
def page_not_found(e):
    return redirect('/')


"""""
mqttc = mqtt.Client()
mqttc.connect("192.168.0.15", 1883, 60)
mqttc.loop_start()

je potřeba dodělat CRUD funkce,

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

        if action == "1":
            mqttc.publish(scene+"/"+device+"/"+end_topic + "command", "on")
        if action == "0":
            mqttc.publish(scene+"/"+device+"/"+end_topic + "command", "off")

        return scene + "/" + device + "/" + number[0] + help[0] + "command"

    except:
        pass
"""

from views import auth
app.register_blueprint(auth.bp)

from views import homepage
app.register_blueprint(homepage.bp)

from views import scenes
app.register_blueprint(scenes.bp)

from views import devices
app.register_blueprint(devices.bp)

from views import types
app.register_blueprint(types.bp)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

from werkzeug.security import generate_password_hash

from views import views

import sqlite3

from flask import Flask, render_template, request, flash, redirect, session

app = Flask(__name__)
app.secret_key = "super secret key"


@app.before_request
def load_logged_in_user():
    views.load_logged_in_user()


"""""
mqttc = mqtt.Client()
mqttc.connect("192.168.0.15", 1883, 60)
mqttc.loop_start()
"""
"""
je potřeba dodělat CRUD funkce,
"""""



def get_db_connection():
    ## dodělat ošetření
    conn = sqlite3.connect('db.sqlite')
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/add/")
def add():
    return "nabídka přidání věcí"





# -----------------------------------


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


app.add_url_rule('/', view_func=views.main)

# --------------

app.add_url_rule('/user/add/', view_func=views.user_add, methods=("POST", "GET"))
app.add_url_rule('/user/login/', view_func=views.user_login, methods=("POST", "GET"))
app.add_url_rule('/user/logout/', view_func=views.user_logout)

# -------------

app.add_url_rule('/scenes/', view_func=views.scenes)
app.add_url_rule('/scenes/<int:id>/', view_func=views.scene)
app.add_url_rule('/scenes/<int:id>/edit/', view_func=views.scenes_edit)
app.add_url_rule('/scenes/add/', view_func=views.scenes_add, methods=("POST", "GET"))

# -------------

app.add_url_rule('/devices/', view_func=views.devices)
app.add_url_rule('/devices/<int:id>/', view_func=views.device)
app.add_url_rule('/devices/add/', view_func=views.devices_add, methods=("POST", "GET"))

# ---------------

app.add_url_rule('/types/', view_func=views.types)
app.add_url_rule('/types/<int:id>/', view_func=views.type)
app.add_url_rule('/types/add/', view_func=views.types_add, methods=("POST", "GET"))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

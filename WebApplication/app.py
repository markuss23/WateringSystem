import paho.mqtt.client as mqtt
import sqlite3
from flask import Flask, render_template, request

app = Flask(__name__)


def get_db_connection():
    ## dodělat ošetření
    conn = sqlite3.connect('db.sqlite')
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/")
def main():
    conn = get_db_connection()
    scenes = conn.execute("select * from scene").fetchall()
    conn.close()
    return render_template('index.html', scenes=scenes)

@app.route("/<device>")
def action(device):
    conn = get_db_connection()
    datas = conn.execute("select  device.label as 'device', scene.label as 'scene' from device, scene inner join scene_device sd on device.id = sd.device_id inner join scene s on s.id = sd.scene_id where scene.label = ?", (device, )).fetchall()
    return render_template('device.html', datas=datas)
"""""
@app.route("/<device>/<type>")
def action(type):
    conn = get_db_connection()
    datas = conn.execute("select  device.label as 'device', scene.label as 'scene' from device, scene inner join scene_device sd on device.id = sd.device_id inner join scene s on s.id = sd.scene_id where scene.label = ?", (type, )).fetchall()
    return render_template('device.html', datas=datas)
"""
if __name__ == '__main__':
    app.run()

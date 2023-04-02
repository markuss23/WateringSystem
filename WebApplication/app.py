import json
import logging

import eventlet
from eventlet import wsgi

eventlet.monkey_patch()

from flask import Flask, redirect
from WebApplication.views.mqtt_connector import broker_address
from flask_mqtt import Mqtt
from flask_socketio import SocketIO
from WebApplication.views.db import get_db_connection

app = Flask(__name__)
log = logging.getLogger('werkzeug')
log.disabled = True
app.secret_key = "super secret key"
app.config['SESSION_TYPE'] = 'mqtt_session'
app.config['MQTT_BROKER_URL'] = broker_address
app.config['MQTT_BROKER_PORT'] = 1883
app.config['MQTT_CLIENT_ID'] = 'flask_mqtt'
app.config['MQTT_KEEPALIVE'] = 60
app.debug = False
mqtt = Mqtt(app)
socketio = SocketIO(app)

conn = get_db_connection()


@socketio.on('publish')
def handle_publish(json_str):
    data = json.loads(json_str)
    mqtt.publish(data['topic'], data['message'], data['qos'])


@socketio.on('subscribe')
def handle_subscribe(json_str):
    print('prihlaseno')
    data = json.loads(json_str)
    mqtt.subscribe(data['topic'], data['qos'])


@socketio.on('unsubscribe_all')
def handle_unsubscribe_all():
    mqtt.unsubscribe_all()


@socketio.on('unsubscribe')
def handle_unsubscribe(json_str):
    data = json.loads(json_str)
    mqtt.unsubscribe(data['topic'])


@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
    data = dict(
        topic=message.topic,
        payload=message.payload.decode(),
        qos=message.qos,
    )
    socketio.emit('mqtt_message', data=data)


@mqtt.on_log()
def handle_logging(client, userdata, level, buf):
    # print(level, buf)
    pass


@app.before_first_request
def load_devices():
    devices = conn.execute("select device_topic from device where is_active=1").fetchall()
    for i in range(len(devices)):
        data = {
            'topic': devices[i][0],
            'qos': 1
        }
        handle_subscribe(json.dumps(data))


@app.before_request
def load_logged_in_user():
    auth.load_logged_in_user()


@app.errorhandler(404)
def page_not_found(e):
    return redirect('/')


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

from views import routines

app.register_blueprint(routines.bp)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, use_reloader=False, debug=True, allow_unsafe_werkzeug=True)

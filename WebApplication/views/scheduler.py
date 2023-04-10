import logging
from apscheduler.schedulers.background import BackgroundScheduler
from WebApplication.views.db import get_db_connection
import paho.mqtt.client as Mqtt
from WebApplication.views.mqtt_connector import get_broker

mqtt = Mqtt.Client()


def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))


def on_disconnect(client, userdata, rc):
    print("Disconnected with result code " + str(rc))


mqtt.on_connect = on_connect
mqtt.on_disconnect = on_disconnect

mqtt.connect(get_broker(), 1883)


def get_scheduler():
    scheduler = BackgroundScheduler(daemon=True)
    return scheduler


scheduler = get_scheduler()


def send_mqtt_message(job, topic):
    print(topic, job[2])
    mqtt.publish(topic, job[2])


def run_job(job, topic):
    print("běžím")
    send_mqtt_message(job, topic)


def connect_cron():
    conn = get_db_connection()
    try:
        scheduler.remove_all_jobs()
        routines = conn.execute(
            "select r.id, d.device_topic, r.data, r.label, r.day_of_week, r.hour, r.minute, r.second from routine as r inner join device d on d.id = r.device_id where r.is_active = 1").fetchall()
        for job in routines:
            topic = job[1]
            if "relay" in topic:
                topic = topic + "/command"

            if job[4] == "":
                scheduler.add_job(
                    run_job,
                    'cron',
                    hour=job[5],
                    minute=job[6],
                    second=job[7],
                    args=[job, topic]
                )
            elif job[5] == "":
                scheduler.add_job(
                    run_job,
                    'cron',
                    day_of_week=job[4],
                    minute=job[6],
                    second=job[7],
                    args=[job, topic]
                )
            elif job[6] == "":
                scheduler.add_job(
                    run_job,
                    'cron',
                    day_of_week=job[4],
                    hour=job[5],
                    second=job[7],
                    args=[job, topic]
                )
            elif job[7] == "":
                scheduler.add_job(
                    run_job,
                    'cron',
                    day_of_week=job[4],
                    hour=job[5],
                    minute=job[6],
                    args=[job, topic]
                )
            else:
                scheduler.add_job(
                    run_job,
                    'cron',
                    day_of_week=job[4],
                    hour=job[5],
                    minute=job[6],
                    second=job[7],
                    args=[job, topic]
                )
        print("startuji")
        scheduler.start()
        mqtt.loop_forever()
    except:
        pass

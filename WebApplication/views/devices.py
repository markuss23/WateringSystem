from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from WebApplication.views.auth import login_required
from WebApplication.views.db import get_db_connection

bp = Blueprint('devices', __name__, url_prefix='/devices')

@bp.route('/')
@login_required
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


@bp.route('/<int:id>/')
@login_required
def device(id):
    template_data = {
        'devices': False,
        'scenes': False,
        'types': False,
    }
    try:
        conn = get_db_connection()
        devices = conn.execute(
            "select * from device where device.id = ?",
            (id,)).fetchall()

        scenes = conn.execute(
            "select s.id, s.label, s.scene_topic, s.is_active from scene s join scene_device sd on s.id = sd.scene_id join device d on d.id = sd.device_id where d.id=?;",
            (id,)).fetchall()

        types = conn.execute(
            "select * from type inner join device d on type.id = d.type_id where d.id = ?",
            (id,)).fetchall()

        template_data['devices'] = devices
        template_data['scenes'] = scenes
        template_data['types'] = types
    except:
        pass

    return render_template('device/deviceDetail.html', **template_data)


@bp.route('/add/', methods=("POST", "GET"))
@login_required
def devices_add():
    if g.user['is_supervisor'] != 1:
        return redirect(url_for('devices'))
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
                    return redirect(url_for('main'))
            flash(error)
    except:
        pass

    return render_template('device/deviceAdd.html', **template_data)


@bp.route('/<int:id>/edit/', methods=("POST", "GET"))
@login_required
def devices_edit(id):
    if g.user['is_supervisor'] != 1:
        return redirect(url_for('devices'))

    conn = get_db_connection()
    template_data = {
        'datas': False,
        'types': False
    }

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
                    conn.execute(
                        "UPDATE device SET type_id=?, label = ?, device_topic = ?, is_active = ?, pin=? WHERE device.id = ?",
                        (select, label, device_topic, is_active, pin, id))
                    conn.commit()
                    print("asd")
                except error:
                    error = "chyba při zapsání do Databáze"
                else:
                    return redirect('/devices/')
            flash(error)
    except:
        pass

    try:
        datas = conn.execute("select * from device as s where s.id = ?",
                             (id,)).fetchall()

        types = conn.execute("select * from type")

        template_data['datas'] = datas
        template_data['types'] = types
    except:
        pass

    return render_template('device/deviceEdit.html', **template_data)



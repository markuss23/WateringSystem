from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from WebApplication.views.auth import login_required
from WebApplication.views.db import get_db_connection

bp = Blueprint('routines', __name__, url_prefix='/routines')


@bp.route('/')
@login_required
def routines():
    template_data = {
        'routine': False,
        'label': 'Výpis všech služeb'
    }
    try:
        conn = get_db_connection()
        routines = conn.execute("select * from routine order by is_active desc ").fetchall()
        conn.close()
        template_data['routines'] = routines

    except:
        pass
    return render_template('routine/routineList.html', **template_data)


@bp.route('/<int:id>/')
@login_required
def routine(id):
    template_data = {
        'routines': False,
        'scenes': False,
        'devices': False,
    }
    try:
        conn = get_db_connection()
        routines = conn.execute(
            "select * from routine where routine.id = ?",
            (id,)).fetchall()
        devices = conn.execute(
            "select * from device as d inner join routine as r on d.id = r.device_id where r.id = ?",
            (id,)).fetchall()

        scenes = conn.execute(
            "select s.id, s.label from scene as s join scene_routine sr on s.id = sr.scene_id where sr.is_active=1 and sr.routine_id = ?;",
            (id,)).fetchall()

        conn.close()
        template_data['routines'] = routines
        template_data['scenes'] = scenes
        template_data['devices'] = devices

    except:
        pass

    return render_template('routine/routineDetail.html', **template_data)


@bp.route('/add/', methods=("POST", "GET"))
@login_required
def routines_add():
    if g.user['is_supervisor'] != 1:
        return redirect('/devices/')
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

            if is_active is None:
                is_active = 0
            else:
                is_active = 1

            error = None

            if not label:
                error = 'Název scény chybí'
            if not device_topic:
                error = 'Adresa chybí'

            if error is None:
                try:
                    conn.execute("INSERT INTO device VALUES (NULL,?,?,?,?)",
                                 (select, label, device_topic, is_active))
                    conn.commit()
                except conn.IntegrityError:
                    error = f" Tato adresa již existuje "
                else:
                    return redirect('/devices/')
            flash(error)
    except:
        pass

    return render_template('device/deviceAdd.html', **template_data)


@bp.route('/<int:id>/edit/', methods=("POST", "GET"))
@login_required
def routines_edit(id):
    if g.user['is_supervisor'] != 1:
        return redirect('/devices/')

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

            if is_active is None:
                is_active = 0
            else:
                is_active = 1
            error = None

            if not label:
                error = 'Název scény chybí'
            if not device_topic:
                error = 'Adresa chybí'

            print(error)
            if error is None:
                try:
                    conn.execute(
                        "UPDATE device SET type_id=?, label = ?, device_topic = ?, is_active = ? WHERE device.id = ?",
                        (select, label, device_topic, is_active, id))
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


@bp.route('/<int:id>/', methods=("POST", "GET"))
@login_required
def routines_delete(id):
    if g.user['is_supervisor'] != 1:
        return redirect('/devices/')

    try:
        if request.method == 'POST':
            conn = get_db_connection()
            conn.execute('delete FROM device where id=?;',
                         (id,))
            conn.commit()
            conn.execute('delete from scene_device where device_id = ?;',
                         (id,))
            conn.commit()
            conn.close()
            print(id)
    except:
        pass

    return redirect('/devices/')

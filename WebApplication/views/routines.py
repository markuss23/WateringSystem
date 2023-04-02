from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from WebApplication.views.auth import login_required
from WebApplication.views.db import get_db_connection
from WebApplication.views.scheduler import connect_cron

bp = Blueprint('routines', __name__, url_prefix='/routines')


def getDays(arr):
    days = arr.split(",")
    prep = ""
    for day in days:
        if day == "0":
            return "*"
        else:
            if day == "1":
                prep += "mon,"
            elif day == "2":
                prep += "tue,"
            elif day == "3":
                prep += "wed,"
            elif day == "4":
                prep += "thu,"
            elif day == "5":
                prep += "fri,"
            elif day == "6":
                prep += "sat,"
            else:
                prep += "sun,"
    return prep


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
        return redirect('/routines/')
    template_data = {
        'devices': False,
    }
    conn = get_db_connection()

    devices = conn.execute("select * from device where is_active=1")
    template_data['devices'] = devices

    try:
        if request.method == 'POST':
            label = request.form['label']
            device = request.form.get('devices')
            data = request.form['data']
            days = getDays(request.form.get('days'))
            hours = request.form.get('hours')
            minutes = request.form.get('minutes')
            seconds = request.form.get('seconds')
            is_active = request.form.get('is_active')
            if is_active is None:
                is_active = 0
            else:
                is_active = 1
            if days[len(days) - 1] == ',':
                days = days[:-1]
            error = None

            if not label:
                error = 'Název služby chybí'
            if not data:
                error = 'Data chybí'

            if error is None:
                try:
                    conn.execute("INSERT INTO routine VALUES (NULL,?,?,?,?,?,?,?,?)",
                                 (label, device, days, hours, minutes, is_active, data, seconds))
                    conn.commit()
                    conn.close()
                    connect_cron()
                except conn.IntegrityError:
                    error = f" Tato adresa již existuje "
                else:
                    return redirect('/routines/')
            flash(error)
    except:
        pass

    return render_template('routine/routineAdd.html', **template_data)


@bp.route('/<int:id>/edit/', methods=("POST", "GET"))
@login_required
def routines_edit(id):
    if g.user['is_supervisor'] != 1:
        return redirect('/routines/')

    conn = get_db_connection()
    template_data = {
        'routines': False,
        'devices': False
    }

    try:
        if request.method == 'POST':
            label = request.form['label']
            device = request.form.get('devices')
            data = request.form['data']
            days = getDays(request.form.get('days'))
            hours = request.form.get('hours')
            minutes = request.form.get('minutes')
            seconds = request.form.get('seconds')
            is_active = request.form.get('is_active')
            if is_active is None:
                is_active = 0
            else:
                is_active = 1
            if days[len(days) - 1] == ',':
                days = days[:-1]
            error = None

            if not label:
                error = 'Název služby chybí'
            if not data:
                error = 'Data chybí'
            if error is None:
                try:
                    conn.execute(
                        "UPDATE routine SET label=?, device_id = ?, day_of_week = ?, hour = ?, minute = ?, is_active = ?, data = ?, second = ?  WHERE routine.id = ?",
                        (label, device, days, hours, minutes, is_active, data, seconds, id))
                    conn.commit()
                    conn.close()
                    connect_cron()
                except error:
                    error = "chyba při zapsání do Databáze"
                else:
                    return redirect('/routines/')
            flash(error)
    except:
        pass

    try:
        routines = conn.execute("select * from routine as r where r.id = ?",
                                (id,)).fetchall()

        devices = conn.execute("select * from device where is_active = 1")

        template_data['routines'] = routines
        template_data['devices'] = devices
    except:
        pass

    return render_template('routine/routineEdit.html', **template_data)


@bp.route('/<int:id>/', methods=("POST", "GET"))
@login_required
def routines_delete(id):
    if g.user['is_supervisor'] != 1:
        return redirect('/routines/')

    try:
        if request.method == 'POST':
            conn = get_db_connection()
            conn.execute('delete FROM routine where id=?;',
                         (id,))
            conn.commit()
            conn.execute('delete from scene_routine where routine_id = ?;',
                         (id,))
            conn.commit()
            conn.close()
    except:
        pass

    return redirect('/routines/')

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from WebApplication.views.auth import login_required
from WebApplication.views.db import get_db_connection

bp = Blueprint('scenes', __name__, url_prefix='/scenes')


@bp.route('/')
@login_required
def scenes():
    template_data = {
        'scenes': False,
        'label': 'Výpis všech scén'
    }
    try:
        conn = get_db_connection()
        scenes = conn.execute("select * from scene order by is_active desc ").fetchall()
        conn.close()
        template_data['scenes'] = scenes

    except:
        pass
    return render_template('scene/sceneList.html', **template_data)


@bp.route('/<int:id>/')
@login_required
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
            "select d.id, d.label, d.device_topic, d.is_active FROM device d JOIN scene_device sd ON d.id = sd.device_id JOIN scene s ON s.id = sd.scene_id WHERE s.id=?;",
            (id,)).fetchall()

        template_data['scenes'] = scenes
        template_data['devices'] = devices

    except:
        pass

    return render_template('scene/sceneDetail.html', **template_data)


@bp.route('/add/', methods=("POST", "GET"))
@login_required
def scenes_add():
    if g.user['is_supervisor'] != 1:
        return redirect('/scenes/')
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


@bp.route('/<int:id>/edit/', methods=("POST", "GET"))
@login_required
def scenes_edit(id):
    if g.user['is_supervisor'] != 1:
        return redirect('/scenes/')

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
                    return redirect('/scenes/')
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


@bp.route('/<int:id>/attach/', methods=("POST", "GET"))
@login_required
def scenes_attach(id):
    if g.user['is_supervisor'] != 1:
        return redirect('/scenes/')

    template_data = {
        'scenes': False,
        'devices_available': False,
        'devices_connected': False,
        'devices_deactivated': False
    }
    conn = get_db_connection()
    try:
        if request.method == 'POST':
            print("dotaz poslán")
            select = request.form.get('devices_pair')
            is_active = request.form.get('is_active')
            if request.form.get('deactivate'):
                print("edit")
                conn.execute("update scene_device set is_active = 0 where scene_id = ? AND device_id = ?;",
                             (id, select))
                conn.commit()
                return redirect('/scenes/' + id + 'attach/')
            elif request.form.get('activate'):
                conn.execute("update scene_device set is_active = 1 where scene_id = ? AND device_id = ?;",
                             (id, select))
                conn.commit()
                return redirect('/scenes/' + id + 'attach/')
            else:
                conn.execute("INSERT INTO scene_device VALUES (NULL,?,?,?)",
                             (select, id, is_active))
                conn.commit()
                return redirect('/scenes/' + id + 'attach/')
    except:
        pass

    try:
        scenes = conn.execute(
            "select * from scene where scene.id = ?",
            (id,)).fetchall()

        devices_available = conn.execute(
            "select * from device where (id not in (select device_id from scene_device where scene_id = ? ) and is_active = 1)",
            (id,)).fetchall()

        devices_connected = conn.execute(
            "select * from device where (id in (select device_id from scene_device where scene_id = ? and is_active = 1) and is_active = 1)",
            (id,)).fetchall()

        devices_deactivated = conn.execute(
            "select * from device where (id = (select device_id from scene_device where is_active=0 and scene_id = ?));",
            (id,)).fetchall()

        template_data['scenes'] = scenes
        template_data['devices_available'] = devices_available
        template_data['devices_connected'] = devices_connected
        template_data['devices_deactivated'] = devices_deactivated

    except:
        pass

    return render_template('scene/sceneAttach.html', **template_data)

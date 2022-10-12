import functools
import sqlite3

from flask import Flask, render_template, request, flash, redirect, url_for, session, g
from werkzeug.security import generate_password_hash, check_password_hash


def get_db_connection():
    ## dodělat ošetření
    conn = sqlite3.connect('db.sqlite')
    conn.row_factory = sqlite3.Row
    return conn


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('user_login'))

        return view(**kwargs)
    return wrapped_view


@login_required
def user_add():
    if g.user['is_supervisor'] == 1:

        if request.method == 'POST':
            numbers = [0, 0, 0, 0]
            numbers2 = [0, 0, 0, 0]
            username = request.form['username']
            numbers[0] = request.form['1']
            numbers[1] = request.form['2']
            numbers[2] = request.form['3']
            numbers[3] = request.form['4']

            numbers2[0] = request.form['11']
            numbers2[1] = request.form['12']
            numbers2[2] = request.form['13']
            numbers2[3] = request.form['14']

            pin = str(numbers[0]) + str(numbers[1]) + str(numbers[2]) + str(numbers[3])
            pin2 = str(numbers2[0]) + str(numbers2[1]) + str(numbers2[2]) + str(numbers2[3])
            conn = get_db_connection()
            error = None

            if not username:
                error = 'Username is required.'
            elif not pin:
                error = 'Pin is required.'
            elif len(pin) > 4:
                error = 'Pin je dlouhý'
            elif len(pin) < 4:
                error = 'Pin je krátký'
            elif pin != pin2:
                error = 'Piny se neshodují'


            if error is None:
                try:
                    conn.execute(
                        "INSERT INTO user (username, pin) VALUES (?, ?)",
                        (username, generate_password_hash(pin)),
                    )
                    conn.commit()
                except conn.IntegrityError:
                    error = f"User {username} is already registered."
                else:
                    return redirect(url_for("main"))

            flash(error)
    else:
        return redirect(url_for("main"))
    return render_template('auth/userAdd.html')


def user_login():
    if request.method == 'POST':
        numbers = [0, 0, 0, 0]
        username = request.form['username']
        numbers[0] = request.form['1']
        numbers[1] = request.form['2']
        numbers[2] = request.form['3']
        numbers[3] = request.form['4']

        pin = str(numbers[0])+str(numbers[1])+str(numbers[2])+str(numbers[3])
        conn = get_db_connection()
        error = None
        user = conn.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()
        print(user['pin'])
        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['pin'], pin):
            error = 'Incorrect pin.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('main'))
        flash(error)

    return render_template('auth/userLogin.html')


def user_logout():
    session.clear()
    return redirect(url_for('main'))


def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db_connection().execute(
            "select * from user where id =?",
            (user_id,)
        ).fetchone()


@login_required
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


@login_required
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
            "select d.id, d.label, d.device_topic, d.is_active, d.pin FROM device d JOIN scene_device sd ON d.id = sd.device_id JOIN scene s ON s.id = sd.scene_id WHERE s.id=?;",
            (id,)).fetchall()

        template_data['scenes'] = scenes
        template_data['devices'] = devices

    except:
        pass

    return render_template('scene/sceneDetail.html', **template_data)


@login_required
def scenes_add():
    if g.user['is_supervisor'] != 1:
        return redirect(url_for('scenes'))
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


@login_required
def scenes_edit(id):
    if g.user['is_supervisor'] != 1:
        return redirect(url_for('scenes'))

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


@login_required
def device(id):
    template_data = {
        'devices': False,
        'scenes': False,
        'types': False
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


@login_required
def types():
    template_data = {
        'types': False,
        'label': 'Výpis všech typů'
    }
    try:
        conn = get_db_connection()
        types = conn.execute("select * from type").fetchall()
        conn.close()
        template_data['types'] = types
    except:
        pass
    return render_template('type/typeList.html', **template_data)


@login_required
def type(id):
    template_data = {
        'types': False,
        'devices': False,
    }
    try:
        conn = get_db_connection()
        types = conn.execute(
            "select * from type where type.id = ?",
            (id,)).fetchall()

        devices = conn.execute(
            "select * from device where device.type_id = ?",
            (id,)).fetchall()

        template_data['types'] = types
        template_data['devices'] = devices

    except:
        pass

    return render_template('type/typeDetail.html', **template_data)


@login_required
def types_add():
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

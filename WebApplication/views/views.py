import sqlite3

from flask import Flask, render_template, request, flash, redirect


def get_db_connection():
    ## dodělat ošetření
    conn = sqlite3.connect('db.sqlite')
    conn.row_factory = sqlite3.Row
    return conn


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


def add_scene():
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
            "select d.label, d.device_topic, d.is_active, d.pin FROM device d JOIN scene_device sd ON d.id = sd.device_id JOIN scene s ON s.id = sd.scene_id WHERE s.id=?;",
            (id,)).fetchall()

        template_data['scenes'] = scenes
        template_data['devices'] = devices

    except:
        pass

    return render_template('scene/sceneDetail.html', **template_data)


def edit_scene(id):
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

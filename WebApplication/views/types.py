from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from WebApplication.views.auth import login_required
from WebApplication.views.db import get_db_connection

bp = Blueprint('types', __name__, url_prefix='/types')


@login_required
@bp.route('/')
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
@bp.route('/<int:id>/')
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
@bp.route('/add/', methods=("POST", "GET"))
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
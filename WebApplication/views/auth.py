import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from WebApplication.views.db import get_db_connection
from WebApplication.views.scheduler import connect_cron

bp = Blueprint('auth', __name__, url_prefix='/auth')


def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db_connection().execute(
            "select * from user where id =?",
            (user_id,)
        ).fetchone()


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.user_login'))

        return view(**kwargs)

    return wrapped_view


@bp.route('/add/', methods=('GET', 'POST'))
@login_required
def user_add():
    if g.user['is_supervisor'] == 1:

        if request.method == 'POST':
            username = request.form['username']
            pin = request.form['pin']
            is_supervisor = request.form['is_supervisor']
            conn = get_db_connection()
            error = None

            if is_supervisor is None:
                is_supervisor = 0
            else:
                is_supervisor = 1

            if not username:
                error = 'Chybí jméno'
            elif not pin:
                error = 'Chybí pin'
            elif len(pin) < 4:
                error = 'Pin je krátký'
            elif len(pin) > 4:
                error = 'Pin je dlouhý'

            if error is None:
                try:
                    conn.execute(
                        "INSERT INTO user (username, pin, is_supervisor) VALUES (?, ?, ?)",
                        (username, generate_password_hash(pin), is_supervisor),
                    )
                    conn.commit()
                except conn.IntegrityError:
                    error = f"User {username} is already registered."
                else:
                    return redirect('/')

            flash(error)
    else:
        return redirect('/')
    return render_template('auth/userAdd.html')


@bp.route('/login/', methods=('GET', 'POST'))
def user_login():
    template_data = {
        'users': False
    }

    if request.method == 'POST':
        username_id = request.form.get('users')
        pin = request.form['pin']
        conn = get_db_connection()
        error = None
        user = conn.execute(
            'SELECT * FROM user WHERE id = ?', (username_id,)
        ).fetchone()
        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['pin'], pin):
            error = 'Incorrect pin.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            connect_cron()
            return redirect('/')
        flash(error)

    try:
        conn = get_db_connection()
        users = conn.execute("select * from user").fetchall()
        conn.close()
        template_data['users'] = users
    except:
        pass

    return render_template('auth/userLogin.html', **template_data)


@bp.route('/logout/', methods=('GET', 'POST'))
def user_logout():
    session.clear()
    return redirect(url_for('auth.user_login'))

import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from WebApplication.views.db import get_db_connection

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







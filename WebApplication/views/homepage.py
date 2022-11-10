from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from WebApplication.views.auth import login_required
from WebApplication.views.db import get_db_connection

bp = Blueprint('homepage', __name__, url_prefix='/')


@bp.route('/')
@login_required
def main():
    template_data = {
        'scenes': False,
        'devices': False,
    }
    try:
        conn = get_db_connection()
        scenes = conn.execute("select * from scene where is_active=1").fetchall()
        devices = conn.execute("select * from device where is_active=1").fetchall()

        conn.close()
        template_data['scenes'] = scenes
        template_data['devices'] = devices
    except:
        pass

    return render_template('index.html', **template_data)
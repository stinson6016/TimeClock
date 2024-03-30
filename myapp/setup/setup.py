from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash
from dotenv import set_key
from pathlib import Path
from os import environ

from .. import db
from ..models import Users, Settings
from .webforms import SetupForm

setup = Blueprint('setup', __name__,
                  template_folder='templates')

@setup.route('/', methods=['GET', 'POST'])
def show():
    form = SetupForm()
    if request.method == "POST":
        env_file_path = Path('.env')
        settings = Settings.query.get("1")
        settings.comp_name = form.comp_name.data
        set_key(dotenv_path=env_file_path, key_to_set="COMP_NAME", value_to_set=f'{form.comp_name.data}')
        environ['COMP_NAME'] = form.comp_name.data
        pass_hash = generate_password_hash(form.password1.data)
        new_admin = Users(name=form.name.data, email=form.email.data,
                          admin='y', pw_last=datetime.now(),
                          pass_hash=pass_hash)
        db.session.add(new_admin)
        db.session.commit()
        flash('Login to add Employees')
        return redirect(url_for('records.main'))
    else:
        check_users = Users.query.count()
        if check_users > 0:
            return redirect(url_for('main.home'))
    return render_template('setup.html',
                           form=form)
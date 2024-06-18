from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash
from dotenv import set_key
from pathlib import Path
from os import environ, getenv
from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length

from .. import max_vars
from .. import db
from ..models import Users

setup = Blueprint('setup', __name__,
                  template_folder='templates', 
                  url_prefix='/setup')

@setup.route('/', methods=['GET', 'POST'])
def show():
    form = SetupForm()
    if request.method == "POST":
        env_file_path = Path('.env')
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
        form.comp_name.default = getenv('COMP_NAME')
        form.process()
    return render_template('setup.html',
                           form=form)

class SetupForm(FlaskForm):
    comp_name    = StringField   ("Company's Name", validators=[DataRequired(), Length(max=max_vars.MAX_SET_COMP_NAME)])
    name        = StringField   ("Initial Admin's Name", validators=[DataRequired(), Length(max=max_vars.MAX_NAME)])
    email       = EmailField    ("Admin's Email (Optional)",  validators=[Length(max=max_vars.MAX_EMAIL)])
    password1   = PasswordField ('Password', validators=[DataRequired(), Length(min=max_vars.MIN_PASS_STR, max=max_vars.MAX_PASS_STR)])
    password2   = PasswordField ('Confirm Password', validators=[DataRequired(), Length(min=max_vars.MIN_PASS_STR, max=max_vars.MAX_PASS_STR)])
    submit      = SubmitField   ('Save')
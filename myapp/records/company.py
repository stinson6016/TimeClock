from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required
from dotenv import set_key
from pathlib import Path
from os import path, environ

from .webforms import CompanyEdit
from .. import db
from ..models import Settings

company = Blueprint('company', __name__, 
                    template_folder='templates')

@company.route('/show')
@login_required
def show():
    
    settings = Settings.query.where(Settings.id=='1').first()
    return render_template('company/company.html',
                           settings=settings,
                           page='c')

@company.post('/edit')
@login_required
def edit():
    form = CompanyEdit()
    settings = Settings.query.first()
    
    form.comp_name.default      = settings.comp_name
    form.email_active.default   = settings.email_active
    form.email_server.default   = settings.email_server
    form.email_send.default     = settings.email_send
    form.email_user.default     = settings.email_user
    form.email_pass.default     = settings.email_pass
    form.email_port.default     = settings.email_port
    form.email_secure.default   = settings.email_secure
    form.process()
    return render_template('company/company-edit.html',
                           form=form,
                           settings=settings,
                           page='c')

@company.post('/save')
@login_required
def save():
    form = CompanyEdit()
    settings = Settings.query.first()
    active = '1' if form.email_active.data == True else None
    settings.comp_name = form.comp_name.data
    settings.email_active = active
    settings.email_server = form.email_server.data
    settings.email_send = form.email_send.data
    settings.email_user = form.email_user.data
    settings.email_pass = form.email_pass.data
    settings.email_port = form.email_port.data
    settings.email_secure = form.email_secure.data
    db.session.commit()

    env_active:str = 'y' if form.email_active.data == True else 'n'
    if path.exists('.env'):
            print('found env')
    env_tls:str = 'True' if form.email_secure.data == '1' else 'False'

    env_file_path = Path('.env')
    set_key(dotenv_path=env_file_path, key_to_set="COMP_NAME", value_to_set=form.comp_name.data)
    set_key(dotenv_path=env_file_path, key_to_set="MAIL_SERVER", value_to_set=form.email_server.data)
    set_key(dotenv_path=env_file_path, key_to_set="MAIL_PORT", value_to_set=str(form.email_port.data))
    set_key(dotenv_path=env_file_path, key_to_set="MAIL_USE_TLS", value_to_set=env_tls)
    set_key(dotenv_path=env_file_path, key_to_set="MAIL_USERNAME", value_to_set=form.email_user.data)
    set_key(dotenv_path=env_file_path, key_to_set="MAIL_DEFAULT_SENDER", value_to_set=form.email_send.data)
    if form.email_pass.data:
        set_key(dotenv_path=env_file_path, key_to_set="MAIL_PASSWORD", value_to_set=form.email_pass.data)
    set_key(dotenv_path=env_file_path, key_to_set="EMAIL_ACTIVE", value_to_set=env_active)
    environ['COMP_NAME'] = form.comp_name.data
    # environ['EMAIL_ACTIVE'] = env_active
    return redirect(url_for('records.company.show'))
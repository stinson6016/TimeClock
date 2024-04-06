from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required
from dotenv import set_key
from pathlib import Path
from os import path, environ, getenv

from .webforms import CompanyEdit

company = Blueprint('company', __name__, 
                    template_folder='templates')

@company.route('/show')
@login_required
def show():
    comp_name:str = getenv('COMP_NAME')
    email_active = getenv('EMAIL_ACTIVE')
    email_setup = True if getenv('MAIL_DEFAULT_SENDER') and getenv('MAIL_SERVER') else False
    return render_template('company/company.html',
                           comp_name=comp_name,
                           email_setup=email_setup,
                           email_active=email_active,
                           page='c')

@company.post('/edit')
@login_required
def edit():
    form = CompanyEdit()
    env_tls:str = '1' if getenv('MAIL_USE_TLS') == 'True' else '0'
    form.comp_name.default      = getenv('COMP_NAME')
    form.email_active.default   = True if getenv('EMAIL_ACTIVE') == 'y' else False
    form.email_server.default   = getenv('MAIL_SERVER')
    form.email_send.default     = getenv('MAIL_DEFAULT_SENDER')
    form.email_user.default     = getenv('MAIL_USERNAME')
    form.email_pass.default     = getenv('MAIL_PASSWORD')
    form.email_port.default     = getenv('MAIL_PORT')
    form.email_secure.default   = env_tls
    form.process()
    return render_template('company/company-edit.html',
                           form=form,
                           page='c')

@company.post('/save')
@login_required
def save():
    form = CompanyEdit()
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
    environ['MAIL_SERVER'] = form.email_server.data
    environ['MAIL_PORT'] = str(form.email_port.data)
    environ['MAIL_USE_TLS'] = env_tls
    environ['MAIL_USERNAME'] = form.email_user.data
    environ['MAIL_DEFAULT_SENDER'] = form.email_send.data
    environ['EMAIL_ACTIVE'] = env_active

    return redirect(url_for('records.company.show'))
from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_required, current_user
from datetime import datetime, date

from .webforms import CompanyEdit
from .. import db
from ..models import Settings

company = Blueprint('company', __name__, 
                    template_folder='templates')

@company.route('/show')
@login_required
def show():
    
    settings = Settings.query.where(Settings.id=='1').first()
    print(settings.email_server)
    return render_template('company/company.html',
                           settings=settings)

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
                           settings=settings)

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

    return redirect(url_for('records.company.show'))
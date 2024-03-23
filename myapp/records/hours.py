from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_required, current_user
from datetime import datetime, date

from ..models import Punch, Users

hours = Blueprint('hours', __name__,
                  template_folder='templates')

@hours.route('/show')
@login_required
def show():
    return render_template('hours/hours.html')
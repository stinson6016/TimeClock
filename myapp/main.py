from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import desc

from . import db
from .models import Users, Punch
from .webforms import PunchForm

main = Blueprint("main", __name__)

@main.route("/")
def home ():
    form = PunchForm()
    punches = None
    if current_user.is_authenticated:
        punches = Punch.query.where(Punch.user_id==current_user.id).order_by(desc(Punch.clock_in),desc(Punch.clock_out)).limit(20)
    return render_template("main.html",
                           form=form,
                           punches=punches)


@main.route('/setup')
def setup():
    user = Users.query.where(Users.name == 'Patrick').first()
    user.pass_hash = generate_password_hash('test')
    db.session.commit()
    user = Users.query.where(Users.name == 'Westley').first()
    user.pass_hash = generate_password_hash('test')
    db.session.commit()
    return redirect(url_for('main.home'))
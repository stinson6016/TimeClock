from flask import Blueprint, redirect, url_for, flash
from flask_login import current_user

main = Blueprint("main", __name__)

@main.route("/")
def home ():
    if current_user.is_authenticated and current_user.admin == 'y':
        return redirect(url_for('records.main'))
    return redirect(url_for('clock.home'))

@main.route('/admin/')
def admin():
    flash('please chech your link')
    return redirect(url_for('clock.home'))
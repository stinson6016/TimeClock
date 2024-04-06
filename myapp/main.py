from flask import Blueprint, redirect, url_for, flash

main = Blueprint("main", __name__)

@main.route("/")
def home ():
    return redirect(url_for('clock.home'))

@main.route('/admin/')
def admin():
    flash('please chech your link')
    return redirect(url_for('clock.home'))
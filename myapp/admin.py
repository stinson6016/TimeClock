from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user, login_user, logout_user

from . import db

admin = Blueprint("admin", __name__)

@admin.route('/')
def adminmain():
    return render_template("blank.html")

@admin.route('/login')
def login():
    return "not setup"

@admin.route('/logout')
def logout():
    return "not setup"


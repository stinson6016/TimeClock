from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_required, current_user
from datetime import datetime, date

# from .webforms import
from ..import create_database
from ..models import Users, Punch

company = Blueprint('company', __name__, 
                    template_folder='templates')
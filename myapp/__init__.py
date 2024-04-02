from datetime import date
from dotenv import load_dotenv
from flask import Flask, render_template
from flask_login import LoginManager
from os import path, getenv, environ
import logging

from .extensions import db, mail
from .startup import check_env_file, create_database, spam_logger
from .blueprints import load_blueprints

def create_app():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    check_env_file() # checks for the dotenv file and makes a new one if needed, in startup.py
    load_dotenv()
    
    
    basedir = path.abspath(path.dirname(__name__))
    DB_NAME = getenv('DB_NAME')
    DB_SERVER = path.join(basedir, DB_NAME)
    # DB_SERVER = getenv('DB_SERVER')
    

    SECRET_KEY = getenv('SECRET_KEY')
    MYENV = '' if getenv('DEV_ENV') == None else getenv('DEV_ENV')

    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_SERVER}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # app.config['SQLALCHEMY_DATABASE_URI'] = DB_SERVER
    # app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = SECRET_KEY
    db.init_app(app)
    mail.init_app(app)
    app.config['MAIL_SERVER'] = getenv('MAIL_SERVER')
    app.config['MAIL_PORT'] = getenv('MAIL_PORT')
    app.config['MAIL_USERNAME'] = getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = getenv('MAIL_PASSWORD')
    app.config['MAIL_USE_TLS'] = getenv('MAIL_USE_TLS')
    app.config['MAIL_DEFAULT_SENDER'] = environ.get('MAIL_DEFAULT_SENDER')
    mail.init_app(app)

    from .models import Users
    create_database(app, DB_SERVER) # create database moved to startup.py

    load_blueprints(app) # blueprints loading moves to blueprints.py

    from .models import Users

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'clock.showmain'

    @login_manager.user_loader
    def load_user(user_id):
        return Users.query.get(str(user_id))
    
    @app.context_processor
    def inject_myenv():
        return dict(myenv=MYENV, nav_year=(date.today()).year, nav_company=getenv('COMP_NAME'))
    
    # Invalid URL
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("404.html"), 404

    # Internal Server Error
    @app.errorhandler(500)
    def page_not_found(e):
        return render_template("500.html"), 500
    spam_logger() # ascii art in the logs on start up in startup.py
    return app


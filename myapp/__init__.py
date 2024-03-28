from datetime import date
from dotenv import load_dotenv
from flask import Flask, render_template
from flask_login import LoginManager, current_user
from os import path, getenv
import logging

from .extensions import db, migrate, mail

def create_app():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    # import os
    load_dotenv()
    basedir = path.abspath(path.dirname(__name__))
    DB_NAME = getenv('DB_NAME')
    DB_SERVER = path.join(basedir, DB_NAME)
    # DB_SERVER = os.getenv('DB_SERVER')
    SECRET_KEY = getenv('SECRET_KEY')

    MYENV = '' if getenv('DEV_ENV') == None else getenv('DEV_ENV')

    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_SERVER}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # app.config['SQLALCHEMY_DATABASE_URI'] = DB_SERVER
    # app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = SECRET_KEY
    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)

    from .models import Punch, Users
    create_database(app, DB_SERVER)

    # load blueprints
    from .records.records import records
    from .clock.clock import clock
    from .main import main
    from .setup.setup import setup

    # register blueprints
    app.register_blueprint(records, url_prefix='/records')
    app.register_blueprint(clock, url_prefix='/clock')
    app.register_blueprint(main)
    app.register_blueprint(setup, url_prefix='/setup')

    from .models import Users

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'clock.showmain'

    @login_manager.user_loader
    def load_user(user_id):
        return Users.query.get(str(user_id))
    
    @app.context_processor
    def inject_myenv():
        from .models import Settings
        settings = Settings.query.first()
        return dict(myenv=MYENV, nav_year=(date.today()).year, nav_company=settings.comp_name)
    
    # Invalid URL
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("404.html"), 404

    # Internal Server Error
    @app.errorhandler(500)
    def page_not_found(e):
        return render_template("500.html"), 500
    spamlogger()
    return app

def fix_database():
    from .models import Settings
    new_setting = Settings(comp_name='setup')
    db.session.add(new_setting)
    db.session.commit()

def create_database(app, db_server):
    if not path.exists(db_server):
        logging.info("no database file found")
        with app.app_context():
            db.create_all()
            logging.info("Created database!")
            fix_database()
    else:
        logging.info("Database file already exisits")

def spamlogger():
    from art import text2art
    year=(date.today()).year
    art=text2art('\n TimeClock')
    logging.info(f"\nTime Clock \nMyHosted/app {year}{art}")
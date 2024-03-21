from flask import Flask, render_template
from flask_login import LoginManager, current_user
from dotenv import load_dotenv
from datetime import date

from .extensions import db, migrate, mail

def create_app():
    import os
    load_dotenv()
    DB_SERVER = os.getenv('DB_SERVER')
    SECRET_KEY = os.getenv('SECRET_KEY')

    MYENV = '' if os.getenv('DEV_ENV') == None else os.getenv('DEV_ENV')

    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = DB_SERVER
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = SECRET_KEY
    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)

    # load blueprints
    from .admin import admin
    from .clock import clock
    from .main import main

    # register blueprints
    app.register_blueprint(admin, url_prefix='/admin')
    app.register_blueprint(clock, url_prefix='/clock')
    app.register_blueprint(main)

    from .models import Users

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'admin.login'

    @login_manager.user_loader
    def load_user(user_id):
        return Users.query.get(str(user_id))
    
    @app.context_processor
    def inject_myenv():
        return dict(myenv=MYENV, year=(date.today()).year)
    
    # Invalid URL
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("404.html"), 404

    # Internal Server Error
    @app.errorhandler(500)
    def page_not_found(e):
        return render_template("500.html"), 500

    return app
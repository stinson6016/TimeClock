from datetime import date
from os import path
import logging

from . import db


def check_env_file():
    # make .env file if not found
    # sets the database file to the default file name
    # creates a new secret key
    # creates a new pw reset salt
    from dotenv import set_key
    from pathlib import Path
    import secrets
    if not path.exists('.env'):
        logging.warning('dotenv file missing')
        key = secrets.token_hex()
        salt = secrets.token_hex()
        
        env_file_path = Path('.env')
        env_file_path.touch(mode=0o600, exist_ok=True)
        set_key(dotenv_path=env_file_path, key_to_set="DB_NAME", value_to_set="timeclock.db")
        set_key(dotenv_path=env_file_path, key_to_set="COMP_NAME", value_to_set='Setup')
        set_key(dotenv_path=env_file_path, key_to_set="SECRET_KEY", value_to_set=f'{key}')
        set_key(dotenv_path=env_file_path, key_to_set="PASSWORD_RESET_SALT", value_to_set=f'{salt}')
        set_key(dotenv_path=env_file_path, key_to_set="EMAIL_ACTIVE", value_to_set='n')

def create_database(app, db_server):
    from .models import Punch, Users
    if not path.exists(db_server):
        logging.warning("no database file found")
        with app.app_context():
            db.create_all()
            # need to have a comp_name in the database settings table for the front end to work
            # on setup this will get changed
            logging.info("Created database!")
    else:
        logging.info("Database file already exisits")


def spamlogger():
    # this does nothing but put ascii art in the logs 
    from art import text2art
    year=(date.today()).year
    art=text2art('\n TimeClock')
    logging.info(f"\nTime Clock \nMyHosted/app {year}{art}")

# def email_setup(app):
#     from os import getenv, environ
#     if getenv('MAIL_ACTIVE') == 'y':
#         app.config['MAIL_SERVER'] = getenv('MAIL_SERVER')
#         app.config['MAIL_PORT'] = getenv('MAIL_PORT')
#         app.config['MAIL_USERNAME'] = getenv('MAIL_USERNAME')
#         app.config['MAIL_PASSWORD'] = getenv('MAIL_PASSWORD')
#         app.config['MAIL_USE_TLS'] = getenv('MAIL_USE_TLS')
#         app.config['MAIL_DEFAULT_SENDER'] = environ.get('MAIL_DEFAULT_SENDER')
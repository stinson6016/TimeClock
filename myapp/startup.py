from flask import Flask
from datetime import date
from os import path
import logging

from . import db


def check_env_file() -> None:
    '''Check the dotenv file exists; create with default values if not found'''
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
        set_key(dotenv_path=env_file_path, key_to_set="MAIL_SERVER", value_to_set='')
        set_key(dotenv_path=env_file_path, key_to_set="MAIL_PORT", value_to_set='587')
        set_key(dotenv_path=env_file_path, key_to_set="MAIL_USE_TLS", value_to_set='True')
        set_key(dotenv_path=env_file_path, key_to_set="MAIL_USERNAME", value_to_set='')
        set_key(dotenv_path=env_file_path, key_to_set="MAIL_DEFAULT_SENDER", value_to_set='')
        set_key(dotenv_path=env_file_path, key_to_set="MAIL_PASSWORD", value_to_set='')
        set_key(dotenv_path=env_file_path, key_to_set="LOCAL_FILES", value_to_set='y')

def create_database(app: Flask, db_server: str) -> None:
    from .models import Punch, Users
    if not path.exists(db_server):
        logging.warning("no database file found")
        with app.app_context():
            db.create_all()
            logging.info("Created database!")
    else:
        logging.info("Database file already exisits")


def spam_logger(text: str) -> None:
    '''takes text input and turns into ascii art and write into the logs'''
    # this does nothing but put ascii art in the logs 
    from art import text2art
    year=(date.today()).year
    art=text2art(f'\n {text}')
    logging.info(f"\n{text} \nMyHosted/app {year}{art}")
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from .maxvars import MaxVars

db = SQLAlchemy()
mail = Mail()
max_vars = MaxVars()
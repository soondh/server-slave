from flask import Flask
import redis
from flask_mail import Mail
from flask_session import Session
from flask_wtf import CSRFProtect

from models import db
from flask_cors import CORS


def create_app(config):
    app = Flask(__name__)
    app.config.from_object(config)
    db.init_app(app)
    #CSRFProtect(app)
    Session(app)
    CORS(app)
    mail = Mail(app)
    app.mail = mail
    return app

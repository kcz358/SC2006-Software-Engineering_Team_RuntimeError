from flask import request, Flask, render_template, redirect, g, url_for, session, flash
from flask_wtf import FlaskForm
from flask_mail import Message, Mail
from flask_login import UserMixin, LoginManager, login_required, login_user, logout_user, current_user
from wtforms import StringField, SubmitField, PasswordField, ValidationError
from wtforms.validators import DataRequired, EqualTo, Email, Length, Regexp
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous.serializer import Serializer
import os
from .initDataFrame import combined_df

mail = Mail()
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'main.login'

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = "secret keys"
    #Set your own sql server url based on the user you create and the database you use
    app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://meredydd:password@localhost/db"

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    #Setup Your own smtp mail server here
    #app.config['MAIL_SERVER']=''
    #app.config['MAIL_PORT'] = 
    #app.config['MAIL_USERNAME'] = 
    #app.config['MAIL_PASSWORD'] = 
    #app.config['MAIL_USE_TLS'] = 
    #app.config['MAIL_USE_SSL'] = 
    mail.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    return app



from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, ValidationError
from wtforms.validators import DataRequired, EqualTo, Email, Length, Regexp
from ..models import Userinfo

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField('Login')
    
class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(1,64), 
                                                   Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
               'Usernames must have only letters, numbers, dots or '
               'underscores')])
    password = PasswordField("Password", validators=[DataRequired()])
    confirm = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo('password', message="Password must be the same")])
    email = StringField("E-mail", validators=[DataRequired(), Email(message="Please enter a valid email"), Length(1,64)])
    signup = SubmitField("Sign up")
    
    def validate_email(self, field):
        if Userinfo.query.filter_by(email = field.data).first():
            raise ValidationError("Email already registered")
    def validate_username(self, field):
        if Userinfo.query.filter_by(username = field.data).first():
            raise ValidationError("Username already exists")
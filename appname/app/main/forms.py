from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, ValidationError, SelectField, RadioField
from flask_wtf.file import FileField, FileAllowed
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

class SearchForm(FlaskForm):
    category = SelectField(label="Category", validators=[DataRequired()], choices=[('E-Waste', 'E-Waste'), ('Second-hand goods', 'Second-hand goods'), ('Cash for trash', 'Cash for trash'),('Lighting Waste', 'Lighting Waste')])
    location = StringField(label="Location", validators=[DataRequired()])
    mode = SelectField(label="Mode Of Transport", validators=[DataRequired()], choices=[('walking', 'walking'), ('bicycling', 'bicycling'), ('driving', 'driving'), ('transit', 'transit')])
    search = SubmitField(label="Search")

class FeedbackForm(FlaskForm):
    rating = RadioField('Rating', choices=[('1','1'),('2','2'),('3','3'),('4','4'),('5','5')],validators=[DataRequired()])
    review = StringField("Review", validators=[DataRequired(), Length(1,64)])

    picture = FileField(label="Add a picture", validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    upload = SubmitField(label="Upload file")
    create = SubmitField('Create Feedback')

class CreateFeedbackForm(FlaskForm):
    add = SubmitField('Add Feedback')

class FavouriteForm(FlaskForm):
    location_choice = StringField("Location", validators=[DataRequired(), Length(1, 64)])
    waste_type = RadioField('Type of Waste', choices=[('E-Waste'),('2nd-Hand'),('Cash'),('Lighting')],validators=None)
    

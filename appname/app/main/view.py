from flask import request, render_template, redirect, g, url_for, session, flash
from flask_login import login_required, logout_user, login_user, current_user
from ..mail import send_mail
from . import main
from .forms import LoginForm, RegisterForm, SearchForm
from .. import db
from ..models import Userinfo

@main.before_request
def before_request():
    g.user = None
    if 'username' in session:
        g.user = session['username']

@main.route('/', methods=['GET','POST'])
def main_page():
    return render_template('main_page.html')

@main.route("/logout", methods=['GET', 'POST'])
def logout():
    session.pop('username', None)
    logout_user()
    flash("Log out successful")
    return redirect(url_for("main.main_page"))


@main.route("/login", methods=['GET', 'POST'])
def login():
    form_login = LoginForm()
    #Check whether the data is in correct format
    if request.method == 'POST' and form_login.validate_on_submit():
        session.pop('username', None)
        username = form_login.username.data
        password = form_login.password.data
        user = Userinfo.query.filter_by(username = username).first()
        form_login.username.data = ''
        form_login.password.data = ''
        #Verify the user info
        if user != None and user.verify_password(password):
            login_user(user)
            session['username'] = username
            flash("Login successful")
            return redirect(url_for('main.main_page'))
        else:
            flash("Invalid username or password")
            return render_template("login.html", form = form_login)
    
    return render_template("login.html", form = form_login)

@main.route("/register", methods = ['GET', 'POST'])
def register():
    form_register = RegisterForm()
    if request.method == 'POST' and form_register.validate():
        #Adding new user to the databse
        user = Userinfo(username = form_register.username.data, email = form_register.email.data, password = form_register.password.data)
        db.session.add(user)
        db.session.commit()
        form_register.username.data = ''
        form_register.email.data = ''
        form_register.password.data = ''
        form_register.confirm.data = ''
        #Generate confirmation token
        # token = user.generate_confirmation_token()
        # send_mail(sender = "admin@appname",templates = 'email/confirm',to = user.email, user = user, token = token)
        flash("Create Account successful. A confirmation email has been sent to your email")
        return redirect(url_for("main.login", create_account = True))
    
    return render_template("signup.html", form = form_register)

@main.route("/confirm/<token>")
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        db.session.commit()
        flash('You have confirmed your account. Thanks!')
    else:
        flash('The confirmation link is invalid.')
    return redirect(url_for('main.main_page'))

@main.route("/account")
@login_required
def account():
    return render_template("account.html")

@main.route("/findabin", methods=['GET', 'POST'])
# @login_required
def findBin():
    search_form = SearchForm()
    has_searched = False
    locations_found = False
    category = None
    location = None
    if request.method == 'POST' and search_form.validate():
        category = search_form.category.data
        location = search_form.location.data
        has_searched = True
    return render_template("findBin.html", form=search_form, has_searched= has_searched, searched=(category, location))
from flask import request, render_template, redirect, g, url_for, session, flash, get_template_attribute
from flask_login import login_required, logout_user, login_user, current_user
from ..mail import send_mail
from . import main
from .forms import LoginForm, RegisterForm, SearchForm, FeedbackForm, FavouriteForm
from ..initDataFrame import combined_df
from .. import db
from .. import combined_df
from ..models import Userinfo, Article, Feedback, ResNet, input_transform
from onemapsg import OneMapClient
import pandas
import requests, json
import os
import torch
import numpy as np
import io
from PIL import Image
from app import create_app


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
        #token = user.generate_confirmation_token()
        #send_mail(sender = "admin@appname",templates = 'email/confirm',to = user.email, user = user, token = token)
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

def getcoordinates(address):
    req = requests.get('https://developers.onemap.sg/commonapi/search?searchVal='+address+'&returnGeom=Y&getAddrDetails=Y&pageNum=1')
    resultsdict = eval(req.text)
    if len(resultsdict['results'])>0:
        return resultsdict['results'][0]['LATITUDE'], resultsdict['results'][0]['LONGITUDE']
    else:
        pass

def getRoute(source, dest, mode):
    print("getting route")
    api_key = 'AIzaSyDfTs7og5-oCAavy4pm_fVHBj6HkqaGLyU'
    url = "https://maps.googleapis.com/maps/api/distancematrix/json?"

    payload={}
    headers = {}

    response = requests.request("GET", url+'origins=' + source +
                     '&destinations=' + dest + '&mode=' + mode+
                     '&key=' + api_key, headers=headers, data=payload)
    result = eval(response.text)
    print(response.text)
    return result

def getNearestBin(source, category, mode):
    arrResults = []
    for i in range(len(combined_df)):
        if combined_df['CATEGORY'].iloc[i] == category:
            dest = str(combined_df['LATITUDE'].iloc[i]) + ',' + str(combined_df['LONGITUDE'].iloc[i])
            result = getRoute(source,dest, mode)
            time = result['rows'][0]['elements'][0]['duration']["value"] # in seconds
            arrResults.append((round(time/60),i)) #convert time to minutes
            arrResults.sort()
        i += 1
    formatted_results = []
    temp = []
    for j in range(len(arrResults)):
        temp.append(arrResults[j])
        if j%3 ==0:
            formatted_results.append(temp)
            temp=[]

    if len(temp) !=0:
        formatted_results.append(temp)
    return formatted_results

@main.route("/findabin", methods=['GET', 'POST'])
# @login_required
def findBin():
    search_form = SearchForm()
    has_searched = False
    locations_found = False
    category = None
    location = None
    lat = None
    long = None
    binsArr=None
    if request.method == 'POST' and search_form.validate():
        category = search_form.category.data
        location = search_form.location.data
        mode = search_form.mode.data
        has_searched = True
        lat, long = getcoordinates(location)
        source = str(lat)+','+str(long)
        binsArr = getNearestBin(source, category, mode)
    return render_template("findBin.html", form=search_form, has_searched=has_searched, searched=(category, location), search_results=binsArr, data=combined_df)

#dummy dictionary
labels = {0:"E-waste", 1:"2nd-hand", 2:"lightning waste", 3:"cash for trash"}

@main.route("/inference_sync", methods = ['GET', 'POST'])
def inference_sync():
    model = ResNet(4)
    checkpoints = torch.load("/Users/paulzhang/Downloads/SC2006-Software-Engineering_Team_RuntimeError-main/appname/app/resources/epoch_5", map_location='cpu')
    model.load_state_dict(checkpoints['model_state_dict'])
    model.eval()
    if request.method == 'POST' and 'formFile' in request.files:
        
        print("post successful")
        photo = request.files['formFile']
        print("get file")
        in_memory_file = io.BytesIO()
        photo.save(in_memory_file)
        img = Image.open(in_memory_file)
        img = input_transform(img)
        output = model(img.unsqueeze(0)).reshape(-1)
        output_label = np.argmax(output.detach().numpy())
        generate_text = get_template_attribute("_generate_text.html", "generate_text")
        html = generate_text(labels.get(output_label))
        return html
    return "<p> No result </p>"

@main.route("/map")
def viewMap():

    return render_template("mapView.html")


@main.route('/articles',methods=['GET','POST'])
# @login_required
def articles_page():
    articles=Article.query.all()
    if request.method=='POST':
        articleType=request.form['submit_button']
        if articleType=="article1": 
            return redirect(url_for('article_page',number=1))
        elif articleType=="article2":
            return redirect(url_for('article_page', number=2))
        elif articleType=="article3":
            return redirect(url_for('article_page', number=3))
        elif articleType=="article4":
            return redirect(url_for('article_page', number=4))
        elif articleType=="article5":
            return redirect(url_for('article_page', number=5))
        else:
            return redirect(url_for('article_page', number=6))
    else:
        return render_template('articles.html',articles=articles)

@main.route('/article_<number>',methods=["POST","GET"])
# @login_required
def article_page(number):
    id=int(number)-1
    article=Article.query.all()[id]
    return render_template('article.html',article=article)

def save_image(picture_file):
    app = create_app()
    picture_name = picture_file.filename
    picture_path=os.path.join(app.root_path, 'static/feedbackpics', picture_name)
    picture_file.save(picture_path)
    return picture_name

@main.route("/feedback", methods = ['GET', 'POST'])
@login_required
def feedback():
    form_feedback = FeedbackForm()
    image_file = ""
    if form_feedback.validate_on_submit():
        image_file = save_image(form_feedback.picture.data)
        feedback_to_create = Feedback(rating=form_feedback.rating.data,review=form_feedback.review.data, image_file=image_file)
        db.session.add(feedback_to_create)
        db.session.commit()
        flash("Feedback created successfully!")
        return redirect(url_for('main.main_page'))
    image_url=url_for('static', filename="feedback_pics/"+image_file)
    return render_template("feedback.html", form=form_feedback, image_url=image_url)

@main.route("/favourite", methods=['GET', 'POST'])
@login_required
def favourites():
    form_favourite = FavouriteForm()
    if request.method=="POST": 
        flash("successful in searching u mofo")
    return render_template("favourite.html",form=form_favourite)


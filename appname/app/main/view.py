from flask import request, render_template, redirect, g, url_for, session, flash, get_template_attribute, jsonify
from flask_login import login_required, logout_user, login_user, current_user
from ..mail import send_mail
from . import main
from .forms import LoginForm, RegisterForm, SearchForm, FeedbackForm, FavouriteForm, CreateFeedbackForm, AddFavourites
from ..initDataFrame import combined_df
from .. import db
from .. import combined_df
from ..models import Userinfo, Article, Feedback, Favourites, ResNet, input_transform
from onemapsg import OneMapClient
import pandas
import torch
import numpy as np
from PIL import Image
import io
import requests, json
import os
import torch
import numpy as np
import io
from PIL import Image
import sqlite3
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
        #Uncomment this if you set up your mail server
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

def getAddress(lat,long):
    print("your lat is " + str(lat) + " long is " + str(long))
    token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOjkzNjEsInVzZXJfaWQiOjkzNjEsImVtYWlsIjoibWFyeXNvaGhjQGdtYWlsLmNvbSIsImZvcmV2ZXIiOmZhbHNlLCJpc3MiOiJodHRwOlwvXC9vbTIuZGZlLm9uZW1hcC5zZ1wvYXBpXC92MlwvdXNlclwvc2Vzc2lvbiIsImlhdCI6MTY2NzE4NTc5NCwiZXhwIjoxNjY3NjE3Nzk0LCJuYmYiOjE2NjcxODU3OTQsImp0aSI6ImZmZDNiY2I4NmQ3MjQxYTQyODY1MGQwOWRjZjQwMDg1In0.H0HHboQJMuQz7ShJmv82oOuMsWY_vhoR8RKmJ9HPr38'
    #token expires every 3 days, get a new one at one map api after 3 nov 11am (pls update this date)
    req = requests.get('https://developers.onemap.sg/privateapi/commonsvc/revgeocode?location=' + str(lat) +',' + str(long) +
                       '&token='+ token)
    resultsdict = eval(req.text)
    print(resultsdict)
    if len(resultsdict['GeocodeInfo'])>0:
        if resultsdict['GeocodeInfo'][0]['BUILDINGNAME'] == "null":
            building_name=""
        else:
            building_name= str(resultsdict['GeocodeInfo'][0]['BUILDINGNAME']) + " "
        if resultsdict['GeocodeInfo'][0]['BLOCK'] == "null":
            block=""
        else:
            block= str(resultsdict['GeocodeInfo'][0]['BLOCK']) + " "
        if resultsdict['GeocodeInfo'][0]['ROAD'] == "null":
            road=""
        else:
            road= str(resultsdict['GeocodeInfo'][0]['ROAD']) + " "
        return building_name+block+ road
    else:
        return None

def getRoute(source, dest, mode):
    # print("getting route")
    api_key = 'AIzaSyDfTs7og5-oCAavy4pm_fVHBj6HkqaGLyU'
    url = "https://maps.googleapis.com/maps/api/distancematrix/json?"

    payload={}
    headers = {}

    response = requests.request("GET", url+'origins=' + source +
                     '&destinations=' + dest + '&mode=' + mode+
                     '&key=' + api_key, headers=headers, data=payload)
    result = eval(response.text)
    # print(response.text)
    return result

def getNearestBin(source, category, mode):
    arrResults = []
    for i in range(len(combined_df)):
        tempArr = []
        if combined_df['CATEGORY'].iloc[i] == category:
            dest = str(combined_df['LATITUDE'].iloc[i]) + ',' + str(combined_df['LONGITUDE'].iloc[i])
            result = getRoute(source,dest, mode)
            time = result['rows'][0]['elements'][0]['duration']["value"] # in seconds
            tempArr.append(round(time/60)) #convert time to minutes
            tempArr.append(i)
            if combined_df.iloc[i]['NAME'] == "Lightbulb/Lamp Recycling Points":
                tempArr.append("Lightbulb Lamp Recycling Points.jpg")
            elif combined_df.iloc[i]['NAME'] == "Project Homecoming - Ink and toner recycling":
                tempArr.append("Project Homecoming - Ink and toner recycling.jpg")
            elif combined_df.iloc[i]['NAME'] == "NEA Producer Responsibility Scheme - ALBA E-waste Recycling Programme":
                tempArr.append("E-waste millenia walk.png")
            elif combined_df.iloc[i]['NAME'] == "Cash for Trash Station":
                tempArr.append("Cash for Trash Station.jpg")
            elif combined_df.iloc[i]['NAME'] == "PC Dreams":
                tempArr.append("PC Dreams.jpg")
            elif combined_df.iloc[i]['NAME'] == "The Salvation Army":
                tempArr.append("The Salvation Army.jpg")
            elif combined_df.iloc[i]['NAME'] == "MINDS Shop":
                tempArr.append("MINDS Shop.jpg")
            elif combined_df.iloc[i]['NAME'] == "Cash Converters":
                tempArr.append("Cash Converters.jpg")
            elif combined_df.iloc[i]['NAME'] == "Touch Community Services: 301 Thrift Mart":
                tempArr.append("Touch Community Services.png")
            arrResults.append(tempArr)
            arrResults.sort()
        i += 1
    # print(arrResults)
    formatted_results = []
    temp = []
    for j in range(len(arrResults)):
        temp.append(arrResults[j])
        if j%3 ==0:
            formatted_results.append(temp)
            temp=[]

    if len(temp) !=0:
        formatted_results.append(temp)

    # print(formatted_results)
    return formatted_results

def getCurrentLocation():
    api_key = 'AIzaSyDfTs7og5-oCAavy4pm_fVHBj6HkqaGLyU'
    url = "https://www.googleapis.com/geolocation/v1/geolocate?key="

    payload = {}
    headers = {}
    try:
        response = requests.request("POST", url + api_key, headers=headers, data=payload)
        result = eval(response.text)
        # print(result['location']['lat'], result['location']['lng'])
        return result['location']['lat'], result['location']['lng']
    except:
        flash("Unable to get your address! Enter an address or try again!")
        return None

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
    source_string = None
    binsArr=None
    success = False


    if search_form.validate() and request.method == 'POST'  :
        print("YESSS")
        category = search_form.category.data
        isCurrentLocation = search_form.isCurrentLocation.data
        print("location data "+ search_form.location.data)
        try:
            if isCurrentLocation == False:
                location = search_form.location.data
                lat, long = getcoordinates(location)
                success = True

            else:
                print("getting your location")
                lat, long = getCurrentLocation()

                if (lat != None and long != None):
                    location = getAddress(lat, long)
                    success=True
                    flash("Current location is: " + location)

            mode = search_form.mode.data
            has_searched = True
            if success==True:
                source_string = str(lat)+','+str(long)
                binsArr = getNearestBin(source_string, category, mode)
                # print(binsArr)

        except:
            flash('No location found! Please try again.')


    return render_template("findBin.html", search_form=search_form, has_searched=has_searched, searched=(category, location), search_results=binsArr, data=combined_df, lat_source=lat, long_source=long, source_string = source_string)



#dummy dictionary
labels = {0:"E-waste", 1:"2nd-hand", 2:"lightning waste", 3:"cash for trash"}

@main.route("/inference_sync", methods = ['GET', 'POST'])
def inference_sync():
    model = ResNet(4)
    #Fill the checkpoints path according to your path where you put the model checkpoints
    checkpoints = torch.load("resources/epoch_5", map_location='cpu')
    model.load_state_dict(checkpoints['model_state_dict'])
    model.eval()
    if request.method == 'POST' and 'formFile' in request.files:
        
        # print("post successful")
        photo = request.files['formFile']
        # print("get file")
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

#dummy dictionary
labels = {0:"E-waste", 1:"2nd-hand", 2:"lightning waste", 3:"cash for trash"}


@main.route("/findabin/thisbin", methods = ['GET', 'POST'])
def thisBinPage():
    my_var = request.args.get('my_var', None)
    source_string = request.args.get('source_string', None)
    lat_source = request.args.get('lat_source', None)
    long_source = request.args.get('long_source', None)
    lat_destination = combined_df.iloc[int(my_var)]['LATITUDE']
    long_destination = combined_df.iloc[int(my_var)]['LONGITUDE']
    print(lat_source)
    print(long_source)
    zoom = "17"
    url_base = "https://developers.onemap.sg/commonapi/staticmap/getStaticImage?layerchosen=default&lat="
    url = url_base + str(lat_destination) + "&lng=" + str(long_destination) + "&zoom=" + zoom + "&height=512&width=512" + "&polygons=&lines=&points=[" + str(lat_destination) + "," + str(long_destination) + ",\"175,50,0\",\"A\"]" + "|[" + lat_source + "," + long_source + ",\"255,255,178\",\"B\"]&color=&fillColor="

    form_favourite = AddFavourites()
    if form_favourite.validate_on_submit():
        if not current_user.is_authenticated:
            flash("Login Required!")
            return redirect(url_for('main.login'))
        check_add_dict = changeSQL_to_dict(combined_df.iloc[int(my_var)]['CATEGORY'])
        for dicts in check_add_dict:
            if combined_df.iloc[int(my_var)]['ADDRESSPOSTALCODE'] in dicts['location_postal'] and current_user.email == dicts['user_email']:
                flash("Favourites has already been added!")
                break
        else:
            favourites_to_add = Favourites(category=combined_df.iloc[int(my_var)]['CATEGORY'],location_name=combined_df.iloc[int(my_var)]['NAME'],
                                           location_postal=combined_df.iloc[int(my_var)]['ADDRESSPOSTALCODE'],location_streetname=combined_df.iloc[int(my_var)]['ADDRESSSTREETNAME'],
                                           user_email=current_user.email)
            db.session.add(favourites_to_add)
            db.session.commit()
            flash("Favourites Added!")
    return render_template('thisBin.html', my_var = int(my_var), data = combined_df,form=form_favourite, source_string = source_string, url=url)


@main.route("/map")
def viewMap():
    lat_destination = "1.28797431732068"
    long_destination = "103.805808773108"
    lat_source = "1.2940154"
    long_source = "103.8509586"
    zoom = "17"
    url_base = "https://developers.onemap.sg/commonapi/staticmap/getStaticImage?layerchosen=default&lat="
    # response = requests.request("GET", url + lat_destination + "&lng=" + long_destination + "&zoom=" + zoom + "&height=512&width=512" + "&polygons=&lines=&points=[" + lat_destination +","+ long_destination
    #                             +",\"175,50,0\",\"E\"" + "|[" + lat_source + "," + long_source + "\"255,255,178\",\"S\"]&color=&fillColor=")
    # url = "https://developers.onemap.sg/commonapi/staticmap/getStaticImage?layerchosen=default&lat=1.28797431732068&lng=103.805808773108&zoom=17&height=512&width=400&polygons=&lines=&points=[1.2940154,103.8509586,\"255,255,178\",\"A\"]|[1.28797431732068,103.805808773108,\"175,50,0\",\"B\"]&color=&fillColor="
    url = url_base + lat_destination + "&lng=" + long_destination + "&zoom=" + zoom + "&height=512&width=512" + "&polygons=&lines=&points=[" + lat_destination +","+ long_destination+",\"175,50,0\",\"A\"]" + "|[" + lat_source + "," + long_source + ",\"255,255,178\",\"B\"]&color=&fillColor="
    print(url)
    return render_template("mapView.html", url=url)


@main.route('/articles',methods=['GET','POST'])
# @login_required
def articles_page():
    articles=Article.query.all()
    if request.method=='POST':
        articleType=request.form['submit_button']
        if articleType=="article1": 
            return redirect(url_for('main.article_page',number=1))
        elif articleType=="article2":
            return redirect(url_for('main.article_page', number=2))
        elif articleType=="article3":
            return redirect(url_for('main.article_page', number=3))
        elif articleType=="article4":
            return redirect(url_for('main.article_page', number=4))
        elif articleType=="article5":
            return redirect(url_for('main.article_page', number=5))
        else:
            return redirect(url_for('main.article_page', number=6))
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

def get_dropdown_values():

    myDict = { 'Lighting Waste': [ combined_df["ADDRESSSTREETNAME"].iloc[i] for i in range(518) if combined_df["CATEGORY"].iloc[i] == "Lighting Waste" ],
                'E-waste': [ combined_df["ADDRESSSTREETNAME"].iloc[i] for i in range(518) if combined_df["CATEGORY"].iloc[i] == "E-Waste" ],
                'Cash for Trash': [ combined_df["ADDRESSSTREETNAME"].iloc[i] for i in range(518) if combined_df["CATEGORY"].iloc[i] == "Cash for trash" ],
                'Second-hand Goods': [ combined_df["ADDRESSSTREETNAME"].iloc[i] for i in range(518) if combined_df["CATEGORY"].iloc[i] == "Second-hand goods" ] }
    
    class_entry_relations = myDict
                        
    return class_entry_relations


@main.route('/_update_dropdown')
def update_dropdown():

    # the value of the first dropdown (selected by the user)
    selected_class = request.args.get('selected_class', type=str)

    # get values for the second dropdown
    updated_values = get_dropdown_values()[selected_class]

    # create the value sin the dropdown as a html string
    html_string_selected = ''
    for entry in updated_values:
        html_string_selected += '<option value="{}">{}</option>'.format(entry, entry)

    return jsonify(html_string_selected=html_string_selected)

global selected_entry 
global selected_class

@main.route('/_process_data')
def process_data():
    global selected_class
    selected_class = request.args.get('selected_class', type=str)
    global selected_entry
    selected_entry = request.args.get('selected_entry', type=str)

    return jsonify(random_text="Waste category: {}\n\n Address: {}.".format(selected_class, selected_entry))

@main.route("/feedback", methods = ['GET', 'POST'])
@login_required
def displayFeedback():
    form_addFeedback = CreateFeedbackForm()
    if form_addFeedback.validate_on_submit():
        return redirect(url_for('main.createFeedback'))

    class_entry_relations = get_dropdown_values()

    default_classes = sorted(class_entry_relations.keys())
    default_values = class_entry_relations[default_classes[0]]

    return render_template("displayfeedback.html", form=form_addFeedback, all_classes=default_classes, all_entries=default_values)

@main.route("/feedback/show", methods = ['GET', 'POST'])
@login_required
def showFeedback():
    feedback = []
    temp_db = sqlite3.connect("/Users/matchajam/PycharmProjects/sc2006ultra/appname/app/app.db")

    temp_db.row_factory = sqlite3.Row
    values = temp_db.execute("SELECT * FROM feedbacks WHERE location LIKE '%s'" % selected_entry).fetchall()

    for item in values:
        feedback.append({k: item[k] for k in item.keys()})
    temp_db.close()
    return render_template("showfeedback.html",feedback=feedback, selected_entry=selected_entry, selected_class=selected_class)


@main.route("/feedback/create", methods = ['GET', 'POST'])
@login_required
def createFeedback():
    form_feedback = FeedbackForm()

    class_entry_relations = get_dropdown_values()

    default_classes = sorted(class_entry_relations.keys())
    default_values = class_entry_relations[default_classes[0]]

    image_file = ""
    if form_feedback.validate_on_submit():
        if form_feedback.picture.data == None:
            image_file= "defaultbin.png"
        else:
            image_file = save_image(form_feedback.picture.data)
        feedback_to_create = Feedback(location=selected_entry,rating=form_feedback.rating.data,review=form_feedback.review.data, image_file=image_file)
        db.session.add(feedback_to_create)
        db.session.commit()
        flash("Feedback created successfully!")
        return redirect(url_for('main.main_page'))
    image_url=url_for('static', filename="feedback_pics/"+image_file)
    return render_template("feedback.html", form=form_feedback, image_url=image_url, all_classes=default_classes, all_entries=default_values)


@main.route("/favourite/eWaste", methods=['GET', 'POST'])
@login_required
def favourites_ewaste():
    # print(combined_df)
    form_favourite = FavouriteForm()
    #Check the exact string in combined_df!!
    ewaste_dict = changeSQL_to_dict('E-Waste')
    #Pass in favourites db as data over here instead of combined df
    return render_template("ewasteFavourites.html",data=ewaste_dict)

@main.route("/favourite/secondHand", methods=['GET', 'POST'])
@login_required
def favourite_secondHand():
    secondhand_dict = changeSQL_to_dict('Second-hand goods')
    return render_template("secondHandFavourites.html",data=secondhand_dict)

@main.route("/favourite/cash", methods=['GET', 'POST'])
@login_required
def favourite_cash():
    cash_dict = changeSQL_to_dict('Cash for Trash')
    return render_template("cashFavourites.html",data=cash_dict)

@main.route("/favourite/lighting", methods=['GET', 'POST'])
@login_required
def favourite_lighting():
    lighting_dict = changeSQL_to_dict('Lighting Waste')
    return render_template("lightingFavourites.html",data=lighting_dict)

#So that all the favourites pages can use!
def changeSQL_to_dict(waste_type):
    filtered_list = []
    temp_db = sqlite3.connect("/Users/matchajam/PycharmProjects/sc2006ultra/appname/app/app.db")
    temp_db.row_factory = sqlite3.Row
    #Change this to user and location and category
    values = temp_db.execute("SELECT * FROM favourites WHERE category LIKE '%s'" % waste_type).fetchall()
    for item in values:
        filtered_list.append({k: item[k] for k in item.keys()})
    temp_db.close()
    return filtered_list



from flask_login import UserMixin
from . import db, login_manager
from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous.serializer import Serializer

class Userinfo(UserMixin, db.Model):
    __tablename__ = 'userinfos'
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique = True, nullable=False, index=True)
    confirmed = db.Column(db.Boolean, default = False)
    password_hash = db.Column(db.String(128))
    
    def __repr__(self) -> str:
        return "<id : {} , Username : {}>".format(self.userid, self.username)
    
    @property
    def password(self):
        raise AttributeError("password is not a readable attribute")
    
    #Hash password
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def generate_confirmation_token(self):
        s = Serializer(current_app.config['SECRET_KEY'])
        return s.dumps({'confirm':self.id})
    
    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True
    
class Article(db.Model):
    id=db.Column(db.Integer(),primary_key=True)
    author=db.Column(db.String(),nullable=False)
    date=db.Column(db.String(),nullable=False)
    caption=db.Column(db.String(),nullable=False)
    genre=db.Column(db.String(),nullable=False)
    body=db.Column(db.String(),nullable=True)
    
    def getAuthor(self):
        return self.author
    
    def getDate(self):
        return self.date

    
    def getGenre(self):
        return self.genre

    def getBody(self):
        return self.body

class Feedback(db.Model):
    __tablename__ = 'feedbacks'
    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer, nullable=False)
    review = db.Column(db.String(2000), nullable=False)
    image_file = db.Column(db.String(2000))
    owner_id = db.Column(db.Integer, db.ForeignKey('userinfos.id'))

    def __repr__(self) -> str:
        return "<id : {}, Rating : {}, Review : {}>".format(self.owner_id, self.rating, self.review)

class Favourites(db.Model):
    __tablename__ = 'favourites'
    id = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.String)
    address = db.Column(db.String(2000), nullable=False)
    image = db.Column(db.String(20))
    owner_id_fav = db.Column(db.Integer, db.ForeignKey('userinfos.id'))

    def __repr__(self) -> str:
        return "<id : {}, location : {}, address : {}, image: {} >".format(self.owner_id, self.location, self.address,self.image)
  

@login_manager.user_loader
def load_user(userid):
    return Userinfo.query.get(int(userid))
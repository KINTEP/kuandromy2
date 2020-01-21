#Creating the database
from datetime import datetime
from quandromy import db
from flask_login import UserMixin


class User(db.Model, UserMixin): #The users mixing class helps in user management. We inherit the "is_authenticated" method from here
    """docstring for ."""
    id = db.Column(db.Integer, primary_key = True)
    fullname = db.Column(db.String(100), nullable = False)
    username = db.Column(db.String(20), unique = True, nullable = False)
    email = db.Column(db.String(120), unique = True, nullable = False)
    #sex = db.Column(db.String(), nullable = False)
    country = db.Column(db.String(200), nullable = False)
    password = db.Column(db.String(60), nullable = False)
    image_file = db.Column(db.String(20), nullable = False, default = 'default.png')
    Post = db.relationship('Post', backref = 'author', lazy = True)
    Followers = db.relationship('Followers', backref = 'followed', lazy = True)

    def __repr__(self):
        return f'''
                 User Name: {self.username} \n
                 Email: {self.email} \n
                 '''

class Post(db.Model):
    """docstring forProducts."""
    id = db.Column(db.Integer, primary_key = True)
    date_posted = db.Column(db.DateTime, nullable = False, default = datetime.utcnow())
    title = db.Column(db.String(50), nullable = False)
    describe = db.Column(db.Text, nullable = False)
    picture = db.Column(db.String(20), nullable = False, default = 'default.png')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)

    def __repr__(self):
        return f'''{[self.date_posted, self.title, self.describe, self.picture]}
                 '''

class Followers(db.Model):
    """docstring forProducts."""
    id = db.Column(db.Integer, primary_key = True)
    date_followed = db.Column(db.DateTime, nullable = False, default = datetime.utcnow())
    following = db.Column(db.String())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)

    def __repr__(self):
        return f'{self.following}'


db.create_all()
#db.drop_all()

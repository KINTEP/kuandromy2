#Creating the database
from datetime import datetime
from quandromy import create_app
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from quandromy import db, login_manager
from hashlib import md5
from time import time
from flask_login import current_user
from flask_dance.consumer.storage.sqla import OAuthConsumerMixin, SQLAlchemyStorage
from flask import current_app, url_for
from flask_login import UserMixin, AnonymousUserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
##from quandromy.github import github_blueprint


#app = create_app()

class Permission:
    FOLLOW = 1
    COMMENT = 2
    WRITE = 4
    MODERATE = 8
    ADMIN = 16

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __init__(self, **kwargs):
        super(Role, self).__init__(**kwargs)
        if self.permissions is None:
            self.permissions = 0

    @staticmethod
    def insert_roles():
        roles = {
            'User': [Permission.FOLLOW, Permission.COMMENT, Permission.WRITE],
            'Moderator': [Permission.FOLLOW, Permission.COMMENT,
                          Permission.WRITE, Permission.MODERATE],
            'Administrator': [Permission.FOLLOW, Permission.COMMENT,
                              Permission.WRITE, Permission.MODERATE,
                              Permission.ADMIN],
        }
        
        default_role = 'User'
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.reset_permissions()
            for perm in roles[r]:
                role.add_permission(perm)
            role.default = (role.name == default_role)
            db.session.add(role)
        db.session.commit()

    def add_permission(self, perm):
        if not self.has_permission(perm):
            self.permissions += perm

    def remove_permission(self, perm):
        if self.has_permission(perm):
            self.permissions -= perm

    def reset_permissions(self):
        self.permissions = 0

    def has_permission(self, perm):
        return self.permissions & perm == perm

    def __repr__(self):
        return '<Role %r>' % self.name

class Follow(db.Model):
    __tablename__ = 'follows'
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'),
                            primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey('users.id'),
                            primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class User(db.Model, UserMixin): #The users mixing class helps in user management. We inherit the "is_authenticated" method from here
    """docstring for ."""
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key = True)
    fullname = db.Column(db.String(100))
    username = db.Column(db.String(20), unique = True, index = True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    email = db.Column(db.String(120), unique = True, index = True)
    country = db.Column(db.String(200))
    #name = db.Column(db.String(64))
    about_me = db.Column(db.Text())
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    image_file = db.Column(db.String(20), default = 'default.png')
    last_message_read_time = db.Column(db.DateTime)
    password = db.Column(db.String(60), nullable = False)
    comments = db.relationship('Comment', backref='author', lazy='dynamic')
    Report = db.relationship('Report', backref='author', lazy='dynamic')
    Post = db.relationship('Post', backref = 'author', lazy = 'dynamic')
    followed = db.relationship('Follow',
                               foreign_keys=[Follow.follower_id],               #SQLAlchemy cannot use the association table transparently because that will not give
                               backref=db.backref('follower', lazy='joined'),   #the application access to the custom fields in it. Instead, the many-to-many relationship
                               lazy='dynamic',                                  #must be decomposed into the two basic one-to-many relationships for the left
                               cascade='all, delete-orphan')                    #and right sides, and these must be defined as standard relationships.
    followers = db.relationship('Follow',
                                foreign_keys=[Follow.followed_id],
                                backref=db.backref('followed', lazy='joined'),
                                lazy='dynamic',
                                cascade='all, delete-orphan')
    messages_sent = db.relationship('Message',
                                    foreign_keys='Message.sender_id',
                                    backref='sender', lazy='dynamic')
    messages_received = db.relationship('Message',
                                        foreign_keys='Message.recipient_id',
                                        backref='recipient', lazy='dynamic')
    

    @staticmethod
    def add_self_follows():
        """
        Unfortunately, you likely have several users in the database who are already created
        and are not following themselves. If the database is small and easy to regenerate, then
        it can be deleted and re-created, but if that is not an option, then adding an update
        function that fixes existing users is the proper solution.
        """
        for user in User.query.all():
            if not user.is_following(user):
                user.follow(user)
                db.session.add(user)
                db.session.commit()

    def __init__(self, **kwargs):
        """
        When users register an account with the application, the correct role should be
        assigned to them. For most users, the role assigned at registration time will be the
        "User" role, as that is the role that is marked as a default. The only exception is made
        for the administrator, who needs to be assigned the "Administrator" role from the
        start. This user is identified by an email address stored in the FLASKY_ADMIN configuration
        variable, so as soon as that email address appears in a registration request it
        can be given the correct role.

        The User constructor first invokes the constructors of the base classes, and if after
        that the object does not have a role defined, it sets the administrator or default role
        depending on the email address.
        """
        super(User, self).__init__(**kwargs)
        if self.role is None:
            #if self.email == current_app.config['FLASKY_ADMIN']:
                #self.role = Role.query.filter_by(name='Administrator').first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()
        self.follow(self)   #Even though the queries are working as designed, most users will expect to see their
                            #own posts when they are looking at those of their friends. The easiest way to address
                            #this issue is to register all users as their own followers at the time they are created.

#To simplify the implementation of roles and permissions, a helper method can be
#added to the User model that checks whether users have a given permission in the
#role they have been assigned. The implementation simply defers to the role methods
#added previously.
#can() and is_administrator()
    def new_messages(self):
        last_read_time = self.last_message_read_time or datetime(1900, 1, 1)
        return Message.query.filter_by(recipient=self).filter(
            Message.timestamp > last_read_time).count()

    def can(self, perm):
        """
        This method added to the User model returns True if the requested permission
        is present in the role, which means that the user should be allowed to perform the
        requested task.
        """
        return self.role is not None and self.role.has_permission(perm)

    def is_administrator(self):
        return self.can(Permission.ADMIN)

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def ping(self):
        """
        The last_seen field is also initialized to the current time upon creation, but it needs
        to be refreshed each time the user accesses the site. A method in the User class can be
        added to perform this update.
        """
        self.last_seen = datetime.utcnow()
        db.session.add(self)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password1):
        return check_password_hash(self.password, password1)

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'],
            algorithm='HS256').decode('utf-8')

    staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)
    
    def follow(self, user):
        if not self.is_following(user):
            f = Follow(follower=self, followed=user)
            db.session.add(f)

    def unfollow(self, user):
        f = self.followed.filter_by(followed_id=user.id).first()
        if f:
            db.session.delete(f)

    def is_following(self, user):
        if user.id is None:
            return False
        return self.followed.filter_by(
            followed_id=user.id).first() is not None

    def is_followed_by(self, user):
        if user.id is None:
            return False
        return self.followers.filter_by(
            follower_id=user.id).first() is not None


    @property
    def followed_posts(self):
        """This will return all posts of followings user"""
        return Post.query.join(Follow, Follow.followed_id == Post.user_id)\
            .filter(Follow.follower_id == self.id)

    def __repr__(self):
        return f'User: {self.username}'

class OAuth(OAuthConsumerMixin, db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    user = db.relationship(User)


class AnonymousUser(AnonymousUserMixin):
    """
For added convenience, a custom AnonymousUser class that implements the can()
and is_administrator() methods is created as well. This will enable the
application to freely call current_user.can() and current_user.is_administrator()
without having to check whether the user is logged in first.
Flask-Login is told to use the application’s custom anonymous user by
setting its class in the login_manager.anonymous_user attribute.
"""
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False

login_manager.anonymous_user = AnonymousUser

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



class Post(db.Model):
    """docstring forProducts."""
    __tablename__ = 'posts'
    __searchable__ = ['title', 'describe']
    id = db.Column(db.Integer, primary_key = True)
    date_posted = db.Column(db.DateTime, nullable = False, default = datetime.utcnow())
    title = db.Column(db.String(50), nullable = False)
    describe = db.Column(db.String, nullable = False)
    picture = db.Column(db.String(20), nullable = False, default = 'default.png')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable = False)
    comments = db.relationship('Comment', backref='post', lazy='dynamic')
    report = db.relationship('Report', backref='report', lazy='dynamic')

    def __repr__(self):
        return f'''{[self.date_posted, self.title]}
                 '''
    
    def to_json(self):
        json_user = {'id': self.id,
        'Author': self.author.fullname,
        'title': self.title,
        'date_posted': self.date_posted,
        'picture': url_for('static', filename = 'postpics/' + self.picture),
        'describe': self.describe}
        return json_user

#This import is here to prevent circular import errors
#from quandromy import RestApi

class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(50))
    #body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    disabled = db.Column(db.Boolean)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))

    def __repr__(self):
        return f'''{self.timestamp, self.body}
                 '''


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    recipient_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def __repr__(self):
        return f'Message: {self.body}'

class Report(db.Model):
    __tablename__ = 'reports'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(50))
    #body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))

    def __repr__(self):
        return f'''{self.timestamp, self.body}
                 '''

#db.create_all()







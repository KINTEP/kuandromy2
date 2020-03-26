#Creating the database
from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from quandromy import db, login_manager
from flask import current_app
from flask_login import UserMixin, AnonymousUserMixin

class Permission:
    FOLLOW = 1
    COMMENT = 2
    WRITE = 4
    MODERATE = 8
    ADMIN = 16

class User(db.Model, UserMixin): #The users mixing class helps in user management. We inherit the "is_authenticated" method from here
    """docstring for ."""
    #__tablename__ = 'user'
    id = db.Column(db.Integer, primary_key = True)
    fullname = db.Column(db.String(100), nullable = False)
    username = db.Column(db.String(20), unique = True, nullable = False)
    email = db.Column(db.String(120), unique = True, nullable = False)
    country = db.Column(db.String(200), nullable = False)
    password = db.Column(db.String(60), nullable = False)
    #..................................
    #location = db.Column(db.String(64))
    #about_me = db.Column(db.Text())
    #member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    #last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    #.................................
    image_file = db.Column(db.String(20), nullable = False, default = 'default.png')
    Post = db.relationship('Post', backref = 'author', lazy = True)
    Followers = db.relationship('Followers', backref = 'followed', lazy = True)
    #role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    #def __init__(self, **kwargs):
    #    super(User, self).__init__(**kwargs)
    #    if self.role is None:
    #        if self.email == current_app.config['FLASKY_ADMIN']:#I am yet to create this in the environment variable
    #            self.role = Role.query.filter_by(name='Administrator').first()
    #    if self.role is None:
    #        self.role = Role.query.filter_by(default=True).first()

    #Working with generating password
    def get_reset_token(self, expires_sec=1800):
        s = Serializer(current_app.config["SECRET_KEY"], expires_sec)
        return s.dumps({"user_id": self.id}).decode("utf-8")

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config["SECRET_KEY"])
        try:
            user_id = s.loads(token)["user_id"]
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f'''
                 User Name: {self.username} \n
                 Email: {self.email} \n
                 '''
#This functions has something to do with assigning roles
    def can(self, perm):
        return self.role is not None and self.role.has_permission(perm)

    def is_administrator(self):
        return self.can(Permission.ADMIN)

class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False
    def is_administrator(self):
        return False

login_manager.anonymous_user = AnonymousUser

class Post(db.Model):
    """docstring forProducts."""
    #__tablename__ = 'post'
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
    #__tablename__ = 'followers'
    id = db.Column(db.Integer, primary_key = True)
    date_followed = db.Column(db.DateTime, nullable = False, default = datetime.utcnow())
    following = db.Column(db.String())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)

    def __repr__(self):
        return f'{self.following}'

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    #users = db.relationship('User', backref='role', lazy='dynamic')

    def __init__(self, **kwargs):
        super(Role, self).__init__(**kwargs)
        if self.permissions is None:
                self.permissions = 0

#The following methods will manage permissions
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

#This methods has more advantage in case of unit testing
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


#db.create_all()
#db.drop_all()

#Creating the database
from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from quandromy import db, login_manager
#from quandromy import app
from flask import current_app
from flask_login import UserMixin, AnonymousUserMixin

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
    fullname = db.Column(db.String(100), nullable = False)
    username = db.Column(db.String(20), unique = True, nullable = False, index = True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    email = db.Column(db.String(120), unique = True, nullable = False, index = True)
    country = db.Column(db.String(200))
    about_me = db.Column(db.Text())
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    #avatar_hash = db.Column(db.String(32))
    image_file = db.Column(db.String(20), nullable = False, default = 'default.png')
    password = db.Column(db.String(60), nullable = False)
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
    comments = db.relationship('Comment', backref='author', lazy='dynamic')

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
            if self.email == current_app.config['FLASKY_ADMIN']:
                self.role = Role.query.filter_by(name='Administrator').first()
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

    def can(self, perm):
        """
        This method added to the User model returns True if the requested permission
        is present in the role, which means that the user should be allowed to perform the
        requested task.
        """
        return self.role is not None and self.role.has_permission(perm)

    def is_administrator(self):
        return self.can(Permission.ADMIN)

    def ping(self):
        """
        The last_seen field is also initialized to the current time upon creation, but it needs
        to be refreshed each time the user accesses the site. A method in the User class can be
        added to perform this update.
        """
        self.last_seen = datetime.utcnow()
        db.session.add(self)
    
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
        return Post.query.join(Follow, Follow.followed_id == Post.author_id)\
            .filter(Follow.follower_id == self.id)

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
    id = db.Column(db.Integer, primary_key = True)
    date_posted = db.Column(db.DateTime, nullable = False, default = datetime.utcnow())
    title = db.Column(db.String(50), nullable = False)
    describe = db.Column(db.String, nullable = False)
    picture = db.Column(db.String(20), nullable = False, default = 'default.png')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable = False)
    comments = db.relationship('Comment', backref='post', lazy='dynamic')

    def __repr__(self):
        return f'''{[self.date_posted, self.title, self.describe, self.picture]}
                 '''


class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    disabled = db.Column(db.Boolean)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))

 

db.create_all()




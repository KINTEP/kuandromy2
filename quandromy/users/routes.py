from flask import  render_template, url_for, redirect, flash, request, abort
from flask_login import login_user, current_user, logout_user, login_required
from quandromy.users.forms import (RegistrationForm, LoginForm, UpdateAccountForm, 
                RequestResetPassword, ResetPasswordForm, MessageForm)
from quandromy import bcrypt, db,login_manager
from quandromy.database import User, Follow, Post, Permission, Message
from quandromy.users.utils import save_picture, save_picture2, send_email
from . import users
from ..decorators import admin_required, permission_required
from datetime import datetime

"""
@users.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()
        if request.endpoint \
                and request.blueprint != 'users' \
                and request.endpoint != 'static':
            return redirect(url_for('users.unconfirmed'))
"""
@users.before_request
def before_request():
    """This records the time of the user immediately he logs in"""
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@users.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous:
        return redirect(url_for('main.index'))
    return render_template('users/unconfirmed.html')

@users.route("/register", methods = ["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hash_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(fullname = form.fullname.data, username = form.username.data, email = form.email.data,
        image_file = form.picture.data, password = hash_password)
        db.session.add(user)
        db.session.commit()
        user = User.query.filter_by(email=form.email.data).first()
        #send_email(user)
        flash('You now a member of Quatrix, you can now log in', 'success')
        return redirect(url_for('users.login'))
    return render_template("users/register.html", form = form)

@users.route("/login", methods = ["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            next_page = request.args.get('next') #This has something to do with 'next' parameter as it appears in the url
            return redirect(next) if next_page else redirect(url_for('users.account'))
        else:
            flash("Login unsuccessful, please try again", 'danger')
    return render_template("users/login.html", form = form)


@users.route("/dashboard/<string:username>")
def dashboard(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user)
    image_file = url_for('static', filename = 'img/' + user.image_file)
    return render_template('users/dashboard.html', user = user, posts = posts, image_file = image_file)

@users.route('/logout')
def logout():
    logout_user()
    flash("You have been loged out!")
    return redirect(url_for('users.login'))

@users.route('/account', methods = ["POST", 'GET'])
@login_required
def account():
    post = Post.query.filter_by(author = current_user)
    picture_file = current_user.image_file
    image_file = url_for('static', filename = 'img/' + current_user.image_file)
    return render_template('users/account.html', image_file = image_file, post = post)


@users.route('/update', methods = ['POST', 'GET'])
def update():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
        db.session.commit()
        flash("You account has been updated", 'success')
        return redirect(url_for('users.account'))
    elif request.method =="GET":
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.fullname.data = current_user.fullname
        #form.country.data = current_user.country
    image_file = url_for('static', filename = 'img/' + current_user.image_file)
    return render_template('users/update.html', image_file = image_file, form =form)
    #return render_template('update.html', form = form)

@users.route('/myprofile')
def myprofile():
    image_file = url_for('static', filename = 'img/' + current_user.image_file)
    return render_template('users/myprofile.html',  image_file = image_file)

@users.route("/user/<string:username>")
def user_posts(username):
    #page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user).order_by(Post.date_posted.desc())
    return render_template('users/user_posts.html', posts=posts, user=user)

@login_manager.user_loader #This is reuqired to manage users by their ID's
def load_user(user_id):
    return User.query.get(int(user_id))

"""
@users.route('/follow/<int:user_id>', methods = ['POST', 'GET'])
@login_required
def follow(user_id):
    user = User.query.get_or_404(user_id)
    first = Follow.query.filter_by(following=user.username).first()
    follow = Follow(following = user.username, followed = current_user)
    db.session.add(follow)
    db.session.commit()
    flash(f'You are now following {user.username}', 'success')
    return render_template('main/home3.html', first = first)
"""
@users.route('/follow/<username>')
@login_required
#@permission_required(Permission.FOLLOW)
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    if current_user.is_following(user):
        flash('You are already following this user.')
        return redirect(url_for('main.index', username=username))
    current_user.follow(user)
    db.session.commit()
    flash('You are now following %s.' % username)
    return redirect(url_for('main.index', username=username))

@users.route('/unfollow/<username>')
@login_required
#@permission_required(Permission.FOLLOW)
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    if not current_user.is_following(user):
        flash('You are not following this user.')
        return redirect(url_for('.user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash(f'You unfollowed {username}')
    return redirect(url_for('main.index', username=username))

@users.route('/send_message/<recipient>', methods=['GET', 'POST'])
@login_required
def send_message(recipient):
    user = User.query.filter_by(username=recipient).first_or_404()
    form = MessageForm()
    if form.validate_on_submit():
        msg = Message(sender=current_user, recipient=user,
                      body=form.message.data)
        db.session.add(msg)
        db.session.commit()
        flash(('Your message has been sent.'))
        return redirect(url_for('users.account', username=recipient))
    return render_template('users/send_message.html', form=form, recipient=recipient)

@users.route('/messages')
@login_required
def messages():
    current_user.last_message_read_time = datetime.utcnow()
    db.session.commit()
    messages = current_user.messages_received.order_by(
        Message.timestamp.desc())
    return render_template('users/messages.html', messages=messages)

@users.route("/reset_password", methods = ["GET", "POST"])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RequestResetPassword()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_email(user)
        flash("An email has been sent with instructions to reset password", "info")
        return redirect(url_for("users.login"))
    return render_template('users/reset_request.html', form = form)

@users.route("/reset_password/<token>", methods = ["GET", "POST"])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    user = User.verify_reset_token(token)
    if user is None:
        flash("That is an invalid or expired token", "warning")
        return redirect(url_for("users.reset_request"))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hash_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password =  hash_password
        db.session.add(user)
        db.session.commit()
        flash('Your password has been updated, you are now able to log in', 'success')
        return redirect(url_for('users.login'))
    return render_template('users/reset_token.html', form = form)

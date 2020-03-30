from flask import render_template, request, redirect, url_for
from flask_login import current_user
from quandromy.database import Post, User
from . import main
from quandromy.users.forms import LoginForm
from flask_login import login_required
from quandromy import bcrypt
from flask_login import login_user

@main.route("/index", methods = ["GET", "POST"])
def index():
    Users = User.query.all()
    posts = Post.query.order_by(Post.date_posted.desc()).all()
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            next_page = request.args.get('next') #This has something to do with 'next' parameter as it appears in the url
            return redirect(next) if next_page else redirect(url_for('users.account'))
        else:
            flash("Login unsuccessful, please try again or register", 'danger')
    return render_template('main/home4.html', posts = posts, Users= Users, form = form)

@main.route('/about')
def about():
	return render_template('main/about.html')

@main.route('/api_page')
def api_page():
	return render_template('main/api_page.html')

"""
@main.route('/', methods = ["GET", "POST"])
def main():
    if not current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    return render_template('main/main.html', form = form)
"""
    
        
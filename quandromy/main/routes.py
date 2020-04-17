from flask import render_template, request, redirect, url_for, session, flash, g, jsonify
from flask_login import current_user
from quandromy.database import Post, User, Comment
from . import main
from quandromy.users.forms import LoginForm, CommentForm
from quandromy.main.forms import SearchForm
from flask_login import login_required
from quandromy import bcrypt
from flask_login import login_user
from quandromy import db
from datetime import datetime

@main.before_request
def before_request():
    """This records the time of the user immediately he logs in"""
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
        g.search_form = SearchForm()

"""
@main.route("/home", methods = ["GET", "POST"])
def home():
    Users = User.query.all()
    posts = Post.query.order_by(Post.date_posted.desc()).all()
    form = LoginForm()
    form2 = CommentForm()
    if session.get('username'):
        return render_template('main/home3.html')
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            next_page = request.args.get('next') #This has something to do with 'next' parameter as it appears in the url
            return redirect(next) if next_page else redirect(url_for('users.account'))
        else:
            flash("Login unsuccessful, please try again or register", 'danger')
    if form2.validate_on_submit():
        comment = Comment(body = form2.comment)
        db.session.add(comment)
        db.session.commit()
        flash('Commented')
    return render_template('main/home3.html', posts = posts, Users= Users, form = form, form2 = form2)
"""

@main.route("/", methods = ["GET", "POST"])
@main.route("/index", methods = ["GET", "POST"])
def index():
    Users = User.query.all()
    #posts = Post.query.order_by(Post.date_posted.desc()).all()
    posts = current_user.followed_posts.all()
    form = LoginForm()
    """
    comment = Comment()
    if request.method == 'POST':
        comment.body = request.form['comment']
        comment.post = posts.id
        comment.author = current_user
        db.session.add(comment)
        db.session.commit()
        flash('You have commented')
        """
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            next_page = request.args.get('next') #This has something to do with 'next' parameter as it appears in the url
            return redirect(next) if next_page else redirect(url_for('users.account'))
        else:
            flash("Login unsuccessful, please try again or register", 'danger')
    return render_template('main/home4.html', posts = posts, Users= Users, form = form)
"""
@main.route('/comment/<int:postid>')
#@login_required
#@permission_required(Permission.FOLLOW)
def comment(postid):
    post = Post.query.get_or_404(postid)
    return render_template('comment.html', postid = post.id)
"""
@main.route('/comment/<int:postID>', methods = ['GET', 'POST'])
def comment(postID):
    form3 = CommentForm()
    post = Post.query.get_or_404(postID)
    comments = Comment.query.filter_by(post = postID)
    if form3.validate_on_submit():
        comment = Comment(body = form3.comment.data, author = current_user.username, post = post.id)
        db.session.add(comment)
        db.session.commit()
    return render_template('main/comment.html', form3 = form3, 
                postID = post.id, comments = comments, post = post)

@main.route('/search', methods=['POST'])
def search():
    if not g.search_form.validate_on_submit():
        return redirect(url_for('main.index'))
    return redirect(url_for('main.search_results', query=g.search_form.search.data))

@main.route('/search_results/<query>')
def search_results(query):
    results1 = Post.query.whoosh_search(query)
    results2 = User.query.whoosh_search(query)
    return render_template('main/search_results.html',
                           query=query,
                           results=results1,
                           results2 = results2)

@main.route('/about')
def about():
	return render_template('main/about.html')

@main.route('/draw')
def draw():
	return render_template('main/draw.html')

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
    
@main.route('/hide', methods = ["POST"])
def hide():
    id = int(request.form.get('post_id'))
    post_id = Post.query.get_or_404(id)
    return jsonify({"post_id": post_id})


        
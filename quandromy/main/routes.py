from flask import render_template, request, redirect, url_for, session, flash, g, jsonify, make_response
from flask_login import current_user
from quandromy.database import Post, User, Comment
from quandromy.users.forms import LoginForm, CommentForm
from quandromy.main.forms import SearchForm
from flask_login import login_required
from quandromy import bcrypt
from flask_login import login_user
from quandromy import db
from datetime import datetime
from flask import Blueprint


main = Blueprint("main", __name__)


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
@login_required
def index():
    Users = User.query.all()
    #posts = Post.query.order_by(Post.date_posted.desc()).all()
    posts = current_user.followed_posts.all()
    return render_template('main/index2.html', posts = posts, Users= Users)
"""
@main.route('/comment/<int:postid>')
#@login_required
#@permission_required(Permission.FOLLOW)
def comment(postid):
    post = Post.query.get_or_404(postid)
    return render_template('comment.html', postid = post.id)
"""


@main.route('/home5')
def home5():
    return render_template('main/home5.html')

@main.route('/data')
def data():
    Database = Post.query.all()
    AllData = [data.to_json() for data in Database]
    #global Data
    return jsonify({'posts': AllData})


@main.route('/comment', methods = ['GET', 'POST'])
def comment():
    if request.method == "POST":
        body = request.form.get("comment")
        postid = int(request.form.get(id))
        post = Post.query.get_or_404(postid)
        comment = Comment(body = body, author = current_user.username, post = postid)
        db.session.add(comment)
        db.session.commit()
        flash("Your comment has been noticed")

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


@main.route("/load", methods = ['GET','POST'])
def load():

    start = int(request.form.get('start') or 0)
    end =  int(request.form.get('end') or (start + 9))

    Database = Post.query.all()
    Data = [data.to_json() for data in Database]

    if request.form:
        counter = end - start

        if counter == 0:
            print(f"Returning posts 0 to {end}")
            res = make_response(jsonify(db[0: counter]), 200)

        elif counter == len(Data):
            print("No more posts")
            res = make_response(jsonify({}), 200)

        else:
            print(f"Returning posts {start} to {end}")
            res = make_response(jsonify(Data[start: end]), 200)

    return make_response(jsonify(Data[start: end]), 200)

@main.route('/load_post')
def load_post():
    #global Data
    return render_template('main/load_post.html')


        
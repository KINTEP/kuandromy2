from flask import render_template, request, redirect, url_for, session, flash, g, jsonify, make_response
from flask_login import current_user
from quandromy.database import Post, User, Comment, Search
from quandromy.users.forms import LoginForm, CommentForm
from quandromy.main.forms import SearchForm
from flask_login import login_required
from quandromy import bcrypt
from flask_login import login_user
from quandromy import db
from datetime import datetime
from flask import Blueprint
from flask import current_app


main = Blueprint("main", __name__)


@main.before_request
def before_request():
    """This records the time of the user immediately he logs in"""
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
        g.search_form = SearchForm()
    #g.locale = str(get_locale())



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
    comments = Comment.query.all()
    return render_template('main/index2.html', posts = posts, Users= Users, comments = comments)
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
    body = request.form.get("formdata").strip()
    postid =int(request.form.get("postID"))

    ##comments = Comment.query.all()

    if body and postid:
        post = Post.query.get_or_404(postid)
        print(current_user)
        print(post)
        comment = Comment(body = body, author = current_user._get_current_object(), post = post)
        db.session.add(comment)
        db.session.commit()
        flash("Your comment has been noticed")
    else:
        return "No data was received"
    return render_template("main/_comments.html")

@main.route('/allcomments/<int:postid>')
def allcomments(postid):
    comments = Comment.query.filter_by(post = postid).all()
    return render_template("main/_allcomments.html", comments = comments)



@main.route('/search')
@login_required
def search():
    if not g.search_form.validate():
        key_words = search_form.q.data
        search = Search(key_words = key_words, searcher = current_user)
        db.session.add(search)
        db.session.commit()
        return redirect(url_for('main.index'))
    page = request.args.get('page', 1, type=int)
    posts, total = Post.search(g.search_form.q.data, page,
                               current_app.config['POSTS_PER_PAGE'])
    next_url = url_for('main.search', q=g.search_form.q.data, page=page + 1) \
        if total > page * current_app.config['POSTS_PER_PAGE'] else None
    prev_url = url_for('main.search', q=g.search_form.q.data, page=page - 1) \
        if page > 1 else None
    return render_template('main/search_results.html', title= ('Search'), posts=posts,
                           next_url=next_url, prev_url=prev_url)
"""
@main.route('/search_results/<query>')
def search_results(query):
    results1 = Post.query.whoosh_search(query)
    results2 = User.query.whoosh_search(query)
    return render_template('main/search_results.html',
                           query=query,
                           results=results1,
                           results2 = results2)
"""
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


        
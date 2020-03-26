from flask import render_template, request, Blueprint
from quandromy.database import Post, User

main = Blueprint("main", __name__)

@main.route('/',  methods = ["GET", "POST"])
@main.route("/index", methods = ["GET", "POST"])
def index():
    Users = User.query.all()
    posts = Post.query.order_by(Post.date_posted.desc()).all()
    return render_template('main/home3.html', posts = posts, Users= Users)

@main.route('/about')
def about():
	return render_template('main/about.html')

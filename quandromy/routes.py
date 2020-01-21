from flask import  render_template, url_for, redirect, flash, request, abort
from flask_login import login_user, current_user, logout_user, login_required, LoginManager
from quandromy.forms import RegistrationForm, LoginForm, SearchForm, UploadFileForm, UpdateAccountForm, PostForm
from quandromy import app, bcrypt, login_manager, db
from quandromy.database import User, Post, Followers
import secrets
import os
from PIL import Image

@app.route('/',  methods = ["GET", "POST"])
@app.route("/index", methods = ["GET", "POST"])
def index():
    users = User.query.all()
    posts = Post.query.order_by(Post.date_posted).all()
    return render_template('home3.html', posts = posts, users= users)

@app.route("/register", methods = ["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hash_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(fullname = form.fullname.data, username = form.username.data, email = form.email.data,
        image_file = form.picture.data, country=form.country.data, password = hash_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account is created', 'success')
        return redirect(url_for('login'))
    return render_template("register.html", form = form)

@app.route("/login", methods = ["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            next_page = request.args.get('next') #This has something to do with 'next' parameter as it appears in the url
            return redirect(next) if next_page else redirect(url_for('account'))
        else:
            flash("Login unsuccessful, please try again", 'danger')
    return render_template("login.html", form = form)

@app.route("/dashboard")
def dashboard():
    return render_template('dashboard.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

def save_picture(form_picture):
	random_hex = secrets.token_hex(8)
	_, f_ext = os.path.splitext(form_picture.filename)
	picture_fn = random_hex + f_ext
	picture_path = os.path.join(app.root_path, 'static/img', picture_fn)
	#output_size = (5,5)
	i = Image.open(form_picture)
	#i.thumbnail(output_size)
	i.save(picture_path)
	return picture_fn

def save_picture2(form_picture):
	random_hex = secrets.token_hex(8)
	_, f_ext = os.path.splitext(form_picture.filename)
	picture_fn = random_hex + f_ext
	picture_path = os.path.join(app.root_path, 'static/postpics', picture_fn)
	#output_size = (500,500)
	i = Image.open(form_picture)
	#i.thumbnail(output_size)
	i.save(picture_path)
	return picture_fn

@app.route('/account', methods = ["POST", 'GET'])
@login_required
def account():
    image_file = url_for('static', filename = 'img/' + current_user.image_file)
    return render_template('account.html', image_file = image_file)

@app.route('/post/new', methods = ["POST", "GET"])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture2(form.picture.data)
            form.picture.data = picture_file
        post = Post(title = form.title.data, describe = form.describe.data, picture = form.picture.data, author = current_user)
        db.session.add(post)
        db.session.commit()
        flash("Your post has been updated successfully",'success')
        return redirect(url_for("index"))
    return render_template("create_post.html", form = form, legend = 'Create Post')

@app.route('/update', methods = ['POST', 'GET'])
def update():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        db.session.commit()
        flash("You account has been updated", 'success')
        return redirect(url_for('account'))
    elif request.method =="GET":
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.fullname.data = current_user.fullname
        form.country.data = current_user.country
    image_file = url_for('static', filename = 'img/' + current_user.image_file)
    return render_template('update.html', image_file = image_file, form =form)
    #return render_template('update.html', form = form)

@app.route('/about')
def about():
	return render_template('about.html')

@app.route('/myprofile')
def myprofile():
    image_file = url_for('static', filename = 'img/' + current_user.image_file)
    return render_template('myprofile.html',  image_file = image_file)

@login_manager.user_loader #This is reuqired to manage users by their ID's
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/update_post/<int:post_id>', methods = ['POST', 'GET'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    form = PostForm()
    if post.author != current_user:
        abort(403)
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture2(form.picture.data)
            form.picture.data = picture_file
        post.title = form.title.data
        post.describe = form.describe.data
        #post.picture = form.picture.data
        db.session.commit()
        flash("You post has been updated", 'success')
        return (redirect(url_for('index', post_id = post.id)))
    if request.method == "GET":
        form.title.data = post.title
        form.describe.data = post.describe
    return render_template('update_post.html', form = form, legend = 'Update Post')

@app.route('/delete_post/<int:post_id>', methods = ['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted', 'success')
    return redirect(url_for('index'))

@app.route('/follow/<int:user_id>', methods = ['POST', 'GET'])
@login_required
def follow(user_id):
    user = User.query.get_or_404(user_id)
    first = Followers.query.filter_by(following=user.username).first()
    #if current_user.is_authenticated:
    #    if first:
            #flash(f"You are already following {user.username}, you can't follow him anymore", 'danger')
            #return redirect(url_for('index'))
        #else:
    follow = Followers(following = user.username, followed = current_user)
    db.session.add(follow)
    db.session.commit()
    flash(f'You are now following {user.username}', 'success')
    return render_template('home3.html', first = first)

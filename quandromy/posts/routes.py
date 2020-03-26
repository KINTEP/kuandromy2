from flask import  render_template, url_for, redirect, flash, request, abort, Blueprint
from flask_login import current_user, login_required
from quandromy.posts.forms import PostForm
from quandromy.database import Post
from quandromy.users.utils import save_picture, save_picture2
from quandromy import db


posts = Blueprint("posts", __name__)

@posts.route('/post/new', methods = ["POST", "GET"])
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
        return redirect(url_for("main.index"))
    return render_template("posts/create_post.html", form = form, legend = 'Create Post')

@posts.route('/update_post/<int:post_id>', methods = ['POST', 'GET'])
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
        return (redirect(url_for('main.index', post_id = post.id)))
    if request.method == "GET":
        form.title.data = post.title
        form.describe.data = post.describe
    return render_template('posts/update_post.html', form = form, legend = 'Update Post')

@posts.route('/delete_post/<int:post_id>', methods = ['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted', 'success')
    return redirect(url_for('main.index'))

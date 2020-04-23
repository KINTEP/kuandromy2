from flask import url_for, send_file, jsonify
from quandromy.database import Post
from io import BytesIO
from flask import Blueprint
from quandromy.database import Post

RestApi = Blueprint("RestApi", __name__)

def get_post_pic(id):
	post = Post.query.get_or_404(id)
	return jsonify(post.to_json())

def get_pic(id):
	post = Post.query.get_or_404(id)
	return send_file(post.picture)
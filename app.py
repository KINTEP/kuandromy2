from quandromy import create_app
#from quandromy.database import User, Comment, Post

app = create_app()

#@app.shell_context_processor
#def make_shell_context():
 #   return {'db': db, 'User': User, 'Post': Post, 'Comment': Comment}

if __name__ == "__main__":
    app.run(debug=True)

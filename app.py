from flask import Flask, render_template, url_for, redirect, flash
from forms import RegistrationForm, LoginForm

app = Flask(__name__)
app.config['SECRET_KEY'] = "3755199dcfb07dfa7c007558f0f591db"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register", methods = ["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        flash(f'{form.username.data} have successfully Registered!')
    return render_template("register.html", form = form)

@app.route("/login", methods = ["GET", "POST"])
def login():
    form = LoginForm()
    return render_template("login.html", form = form)

@app.route("/dashboard")
def dashboard():
    return render_template('dashboard.html')







if __name__ == "__main__":
    app.run(debug=True)

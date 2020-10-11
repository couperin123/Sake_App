from flask import Flask, redirect, url_for, render_template, request, session, flash
from datetime import timedelta
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, ValidationError
from wtforms.validators import InputRequired, Email, Length, EqualTo
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)

app.secret_key="hellohellohello"
app.permanent_session_lifetime = timedelta(minutes=5)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

bootstrap = Bootstrap(app)
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column("id", db.Integer, primary_key=True)
    username = db.Column("username", db.String(15), unique=True)
    email = db.Column("email", db.String(50), unique=True)
    password = db.Column(db.String(80))

    # def __init__(self, username, email):
    #     self.username = username
    #     self.email = email

    def __repr__(self):
        return '<User %r>' % self.username

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('Remember me')

class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=80)])
    confirm  = PasswordField("Confirm password", validators=[InputRequired(),
    Length(min=8,max=80), EqualTo('password', message="Password must match")])

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')

# Home Page
@app.route('/')
def index():
    return render_template("index.html")

# View page
# @app.route("/view")
# def view():
#     return render_template("view.html", values=User.query.all())

# Test Login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                # return redirect(url_for('dashboard'))
                flash("Login Successful!")
                return redirect(url_for('account'))

        # return '<h1>Invalid username or password</h1>'
        flash("Invalid username or password")
        return render_template('login.html', form=form)
        #return '<h1>' + form.username.data + ' ' + form.password.data + '</h1>'

    return render_template('login.html', form=form)

# Test Register page
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash("New account has been created!")
        return redirect(url_for('index'))
        # return '<h1>New user has been created!</h1>'
    #    # return '<h1>' + form.username.data + ' ' + form.email.data + ' ' + form.password.data + '</h1>'

    return render_template('register.html', form=form)

# Login Page
# @app.route('/login', methods=["POST", "GET"])
# def login():
#     if request.method == "POST":
#         session.permanent = True
#         user = request.form["nm"]
#         session["user"] = user
#
#         # check if user already existed
#         found_user = User.query.filter_by(username=user).first()
#         if found_user:
#             session["email"] = found_user.email
#         else:
#             usr = User(user, "")
#             db.session.add(usr)
#             db.session.commit()
#
#         flash("Login Successful!")
#         return redirect(url_for("user"))
#     else:
#         if "user" in session:
#             flash("Already Logged In!")
#             return redirect(url_for("user"))
#
#         return render_template("login.html")

# @app.route('/user', methods=["POST","GET"])
# def user():
#     email = None
#     if "user" in session:
#         user = session["user"]
#
#         if request.method =="POST":
#             email = request.form["email"]
#             session["email"] = email
#             found_user = User.query.filter_by(username=user).first()
#             found_user.email = email
#             db.session.commit()
#             flash("Email was saved!")
#         else:
#             if "email" in session:
#                 email = session["email"]
#
#         return render_template("user.html", email=email)
#
#     else:
#         flash("You are not logged in!")
#         return redirect(url_for("login"))

@app.route('/account')
@login_required
def account():
    return render_template('account.html', name=current_user.username)


# @app.route('/logout')
# def logout():
#     flash(f"You have been logged out", "info")
#     session.pop("user", None)
#     session.pop("email", None)
#     return redirect(url_for("login"))

# Test logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.before_first_request
def create_tables():
    db.create_all()

if __name__ == '__main__':
    if not os.path.exists('db.sqlite'):
        db.create_all()
    app.run(port=33507, debug=True)

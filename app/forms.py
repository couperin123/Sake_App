from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, ValidationError
from wtforms.validators import InputRequired, Email, Length, EqualTo

class SearchForm(FlaskForm):
    search = StringField('', [InputRequired()], render_kw={"placeholder": "Sake Name (in Japanese)"})

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('Remember me') # This may need to be used in the later version

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

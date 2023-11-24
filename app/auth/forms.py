from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from ..models import User


class LoginForm(FlaskForm):
    email = StringField('', validators=[DataRequired(message='Email Address please')])
    password = PasswordField('', validators=[DataRequired(message='Password please')])
    remember_me = BooleanField('remember me')
    submit = SubmitField('submit')


class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64),
                                             Email()])
    username = StringField('Username', validators=[
        DataRequired(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                              'Usernames must have only letters,'
                                              ' dots or underscores')])
    password = PasswordField('Password', validators=[
        DataRequired(), EqualTo('password2', message='Password must match.')])
    password2 = PasswordField('Confirm Password', validators=[DataRequired()])
    submit = SubmitField('Register')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use')


'''class UserInformationForm(FlaskForm):
    username = StringField('Username', render_kw={'placeholder': 'Username'}, validators=[
        DataRequired(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                              'Usernames must have only letters,'
                                              'numbers, dots or underscores')])
    Firstname = StringField('Firstname', render_kw={'placeholder': 'San'}, validators=[DataRequired(), Length(1, 64)])
    Lastname = StringField('Lastname', render_kw={'placeholder': 'Zhang'}, validators=[DataRequired(), Length(1, 64)])
    Birthday = StringField('Birthday', render_kw={'placeholder': 'January 1st'},
                           validators=[DataRequired(), Length(1, 64)])
    PersonalizedSignature = TextAreaField('PersonalizedSignature', render_kw={'placeholder': 'Good'},
                                          validators=[DataRequired(), Length(0, 500)])
    submit = SubmitField('save changes')
    UploadPortrait = SubmitField('change portrait')'''

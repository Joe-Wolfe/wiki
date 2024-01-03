from wtforms import Form, StringField, TextAreaField, PasswordField, validators, HiddenField
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional


class UserAddForm(FlaskForm):
    """Form for adding users."""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])
    confirm = PasswordField('Confirm Password', validators=[
                            DataRequired(), EqualTo('password', message='Passwords must match')])
    email = StringField('Email', validators=[DataRequired(), Email()])
    character_name = StringField('Character Name', validators=[DataRequired()])


class UserLoginForm(FlaskForm):
    """Form for logging in users."""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])


class CategoryForm(FlaskForm):
    """Form for adding categories."""

    name = StringField('Name', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[Optional()])
    created_by = HiddenField('Created By', validators=[DataRequired()])

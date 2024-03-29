from wtforms import Form, StringField, TextAreaField, PasswordField, validators, HiddenField, SelectField
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional


class UserAddForm(FlaskForm):
    """Form for adding users."""

    username = StringField('Username', validators=[
                           DataRequired(), Length(max=20)])
    password = PasswordField('Password', validators=[Length(min=6)])
    confirm = PasswordField('Confirm Password', validators=[
                            DataRequired(), EqualTo('password', message='Passwords must match')])
    email = StringField('Email', validators=[
                        DataRequired(), Email(), Length(max=50)])
    character_name = StringField('Character Name', validators=[
                                 DataRequired(), Length(max=30)])


class UserEditForm(FlaskForm):
    """Form for editing users."""

    username = StringField('Username', validators=[
                           DataRequired(), Length(max=20)])
    email = StringField('Email', validators=[
                        DataRequired(), Email(), Length(max=50)])
    character_name = StringField('Character Name', validators=[
                                 DataRequired(), Length(max=30)])
    bio = TextAreaField('Bio', validators=[Optional()])
    confirm_password = PasswordField('Confirm Password', validators=[
                                     DataRequired(), Length(min=6)])


class UserLoginForm(FlaskForm):
    """Form for logging in users."""

    username = StringField('Username', validators=[
                           DataRequired(), Length(max=20)])
    password = PasswordField('Password', validators=[Length(min=6)])


class CategoryForm(FlaskForm):
    """Form for adding categories."""

    name = StringField('Name', validators=[DataRequired(), Length(max=30)])
    description = TextAreaField('Description', validators=[Optional()])
    created_by = HiddenField('Created By', validators=[DataRequired()])


class PageForm(FlaskForm):
    """Form for adding pages."""

    title = StringField('Title', validators=[DataRequired(), Length(max=100)])
    category_id = SelectField('Category', validators=[DataRequired()])
    synopsis = TextAreaField('Synopsis', validators=[
                             Optional(), Length(max=280)])
    created_by = HiddenField('Created By', validators=[DataRequired()])


class SectionForm(FlaskForm):
    """Form for adding sections."""

    title = StringField('Title', validators=[DataRequired(), Length(max=100)])
    position = HiddenField('Position', validators=[DataRequired()])
    body = TextAreaField('Content', validators=[Optional()])

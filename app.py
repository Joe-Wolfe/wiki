import os

from flask import Flask, render_template, request, flash, redirect, session, g
from sqlalchemy.exc import IntegrityError
from sqlalchemy import or_

# from forms import UserAddForm, LoginForm, MessageForm, EditUserForm
from models import db, connect_db, Users, Categories, Pages, Sections, searchIndexes

CURR_USER_KEY = "curr_user"

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql:///wiki'))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")
app.app_context().push()
connect_db(app)


@app.route('/')
def home():
    """Show homepage."""

    return render_template('home.html')

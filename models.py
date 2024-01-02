from datetime import datetime

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
db = SQLAlchemy()


def connect_db(app):
    """Connect this database to provided Flask app.

    You should call this in your Flask app.
    """

    db.app = app
    db.init_app(app)
    db.create_all()


class User(db.Model):
    """Users in the system."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    character_name = db.Column(db.String(30), nullable=False)

    @classmethod
    def signup(cls, username, password, email, character_name):
        """Sign up user.
        Hashes password and adds user to system.
        """

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            password=hashed_pwd,
            email=email,
            character_name=character_name,
        )

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        """Find user with `username` and `password`.
        If can't find matching user or if password is wrong, returns False.
        If user is found and password is correct, returns user instance.
        """

        user = User.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password, password):
            return user
        else:
            return False


class Category(db.Model):
    """Categories in the wiki."""

    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    category = db.Column(db.String(30), nullable=False, unique=True)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False,
                           default=datetime.utcnow)
    created_by = db.Column(
        db.Integer, db.ForeignKey('users.id',), nullable=False)


class Page(db.Model):
    """Pages in the wiki."""

    __tablename__ = "pages"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False, unique=True)
    synopsis = db.Column(db.String(280), nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False,
                           default=datetime.utcnow)
    created_by = db.Column(
        db.Integer, db.ForeignKey('users.id',), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey(
        'categories.id',), nullable=False)


class Section(db.Model):
    """Sections in the wiki."""

    __tablename__ = "sections"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False, unique=True)
    body = db.Column(db.Text, nullable=False)
    position = db.Column(db.Integer, nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False,
                           default=datetime.utcnow)
    created_by = db.Column(
        db.Integer, db.ForeignKey('users.id',), nullable=False)
    page_id = db.Column(db.Integer, db.ForeignKey('pages.id',), nullable=False)


class searchIndex(db.Model):
    """Search indexes for the wiki."""

    __tablename__ = "searchIndexes"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    in_title = db.Column(db.Boolean, nullable=False, default=True)
    word_count = db.Column(db.Integer, nullable=False)
    page_id = db.Column(db.Integer, db.ForeignKey('pages.id',), nullable=False)

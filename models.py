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


class Users(db.Model):
    """Users in the system."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    character_name = db.Column(db.String(30), nullable=False)


class Categories(db.Model):
    """Categories in the wiki."""

    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    category = db.Column(db.String(30), nullable=False, unique=True)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False,
                           default=datetime.utcnow)
    created_by = db.Column(
        db.Integer, db.ForeignKey('users.id',), nullable=False)


class Pages(db.Model):
    """Pages in the wiki."""

    __tablename__ = "pages"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False, unique=True)
    synopsis = db.Column(db.db.String(280), nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False,
                           default=datetime.utcnow)
    created_by = db.Column(
        db.Integer, db.ForeignKey('users.id',), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey(
        'categories.id',), nullable=False)


class Sections(db.Model):
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


class searchIndexes(db.Model):
    """Search indexes for the wiki."""

    __tablename__ = "searchIndexes"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    in_title = db.Column(db.Boolean, nullable=False, default=True)
    word_count = db.Column(db.Integer, nullable=False)
    page_id = db.Column(db.Integer, db.ForeignKey('pages.id',), nullable=False)

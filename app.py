import os

from flask import Flask, render_template, request, flash, redirect, session, g
from sqlalchemy.exc import IntegrityError
from sqlalchemy import or_

# from forms import UserAddForm, LoginForm, MessageForm, EditUserForm
from models import db, connect_db, User, Category, Page, Section, searchIndex
from forms import UserAddForm, UserLoginForm, CategoryForm
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


#####################################################################
# User signup/login/logout

@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None


def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]


@app.route('/signup', methods=["GET", "POST"])
def signup():
    """Handle user signup.
    Create new user and add to DB. Redirect to homepage.
    If form not valid, present form.
    If there already is a user with that username: flash message
    and re-present form.
    """

    if g.user:
        return redirect('/')

    form = UserAddForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                password=form.password.data,
                email=form.email.data,
                character_name=form.character_name.data,
            )
            db.session.commit()

        except IntegrityError:
            flash("Username already taken!", 'error')
            return render_template('users/signup.html', form=form)

        do_login(user)

        return redirect("/")

    else:
        return render_template('users/signup.html', form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login."""

    if g.user:
        return redirect('/')

    form = UserLoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data,
                                 form.password.data)

        if user:
            do_login(user)
            return redirect("/")
        flash("Invalid credentials.", 'error')

    return render_template('users/login.html', form=form)


@app.route('/logout', methods=["GET"])
def logout():
    """Handle user logout."""
    do_logout()
    return redirect('/')

#####################################################################
# categories


@app.route('/categories')
def show_categories():
    """Show all categories"""
    categories = Category.query.filter_by(
        is_active=True).order_by(Category.name).all()
    return render_template('categories/categories.html', categories=categories)


@app.route('/categories/add', methods=["GET", "POST"])
def add_category():
    """Add a category"""
    if not g.user:
        flash("Access unauthorized.", "error")
        return redirect("/")
    form = CategoryForm()
    if form.validate_on_submit():
        category = Category(
            name=form.name.data,
            description=form.description.data,
            created_by=form.created_by.data
        )
        db.session.add(category)
        db.session.commit()
        return redirect("/categories")
    else:
        form.created_by.data = g.user.id
        return render_template("categories/add_category.html", form=form)


@app.route('/category/<string:category_name>')
def show_category(category_name):
    """Show a category"""
    category = Category.query.filter_by(name=category_name).first()
    pages = Page.query.filter_by(
        category_id=category.id).order_by(Page.title).all()
    return render_template('categories/category.html', category=category, pages=pages)


@app.route('/category/<string:category_name>/edit', methods=["GET", "POST"])
def edit_category(category_name):
    """Edit a category"""
    if not g.user:
        flash("Access unauthorized.", "error")
        return redirect("/")
    category = Category.query.filter_by(name=category_name).first()
    form = CategoryForm(obj=category)
    if form.validate_on_submit():
        category.name = form.name.data
        category.description = form.description.data
        db.session.commit()
        return redirect("/categories")
    else:
        return render_template("categories/edit_category.html", form=form)


@app.route('/category/<string:category_name>/deactivate', methods=["POST"])
def deactivate_category(category_name):
    """deactivates a category"""
    if not g.user:
        flash("Access unauthorized.", "error")
        return redirect("/")
    category = Category.query.filter_by(name=category_name).first()
    category.is_active = False
    db.session.commit()

    return redirect("/categories")


@app.route('/category/<string:category_name>/activate', methods=["POST"])
def activate_category(category_name):
    """activates a category"""
    if not g.user:
        flash("Access unauthorized.", "error")
        return redirect("/")
    category = Category.query.filter_by(name=category_name).first()
    category.is_active = True
    db.session.commit()

    return redirect("/categories")


@app.route('/')
def home():
    """Show homepage."""

    return render_template('home.html')

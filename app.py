import os
import random

from flask import Flask, render_template, request, flash, redirect, session, g, url_for
from sqlalchemy.exc import IntegrityError
from sqlalchemy import or_

from sqlalchemy_searchable import search

# from forms import UserAddForm, LoginForm, MessageForm, EditUserForm
from models import db, connect_db, User, Category, Page, Section
from forms import UserAddForm, UserLoginForm, CategoryForm, PageForm, SectionForm, UserEditForm
from sqlalchemy_searchable import sync_trigger
from sqlalchemy.orm import joinedload


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
with db.engine.connect() as connection:
    sync_trigger(connection, 'sections',
                 'search_vector', ['body'])
    print("synced trigger")


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
            db.session.rollback()
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

    """Unca"""
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

#####################################################################
# pages


@app.route('/pages')
def show_pages():
    """Show all pages"""
    pages = Page.query.filter_by(
        is_active=True).order_by(Page.title).all()
    return render_template('pages/pages.html', pages=pages)


@app.route("/page/add", methods=["GET", "POST"])
def add_page():
    """Add a page"""
    if not g.user:
        flash("Access unauthorized.", "error")
        return redirect("/pages")
    form = PageForm()
    categories = [("", "Choose one")]+[(str(category.id), category.name)
                                       for category in Category.query.filter_by(is_active=True).all()]
    form.category_id.choices = categories
    form.created_by.data = g.user.id

    if form.validate_on_submit():
        page = Page(
            title=form.title.data,
            synopsis=form.synopsis.data,
            created_by=form.created_by.data,
            category_id=form.category_id.data
        )
        db.session.add(page)
        db.session.commit()
        return redirect("/pages")
    else:
        form.created_by.data = g.user.id
        return render_template("pages/add_page.html", form=form)


@app.route("/page/<string:page_title>/edit", methods=["GET", "POST"])
def edit_page(page_title):
    """Edit a page"""
    if not g.user:
        flash("Access unauthorized.", "error")
        return redirect("/pages")
    page = Page.query.filter_by(title=page_title).first()
    form = PageForm(obj=page)
    categories = [("", "Choose one")]+[(str(category.id), category.name)
                                       for category in Category.query.filter_by(is_active=True).all()]
    form.category_id.choices = categories
    if form.validate_on_submit():
        page.title = form.title.data
        page.synopsis = form.synopsis.data
        page.created_by = form.created_by.data
        page.category_id = form.category_id.data
        db.session.commit()
        return redirect("/pages")
    else:
        return render_template("pages/edit_page.html", form=form)


@app.route('/page/<string:page_title>')
def show_page(page_title):
    """Show a page"""
    page = Page.query.filter_by(title=page_title).first()
    sections = Section.query.filter_by(
        page_title=page.title).order_by(Section.position).all()
    forms = [SectionForm(obj=section) for section in sections]
    forms += [SectionForm()]

    return render_template('pages/page.html', page=page, sections=sections, forms=forms)


@app.route('/page/<string:page_title>/addSection', methods=["GET", "POST"])
def add_section(page_title):
    """Add a section to a page"""
    if not g.user:
        flash("Access unauthorized.", "error")
        return redirect("/")
    page = Page.query.filter_by(title=page_title).first()
    form = SectionForm()
    if form.validate_on_submit():
        section = Section(
            title=form.title.data,
            position=form.position.data,
            body=form.body.data,
            created_by=g.user.id,
            page_title=page.title
        )
        db.session.add(section)
        db.session.commit()

        return redirect("/page/" + page_title)
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(
                    f"Error in the {getattr(form, field).label.text} field - {error}")
        return redirect(url_for('show_page', page_title=page.title))


@app.route('/page/<string:page_title>/editSection/<string:section_id>', methods=["GET", "POST"])
def edit_section(page_title, section_id):
    """Edit a section on a page"""
    if not g.user:
        flash("Access unauthorized.", "error")
        return redirect("/")
    page = Page.query.filter_by(title=page_title).first()
    # Fetch the section from the database
    section = Section.query.get(section_id)
    form = SectionForm()
    if form.validate_on_submit():
        section.title = form.title.data
        section.position = form.position.data
        section.body = form.body.data
        section.created_by = g.user.id
        section.page_title = page.title
        db.session.commit()

        return redirect("/page/" + page_title)
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(
                    f"Error in the {getattr(form, field).label.text} field - {error}")
        return redirect(url_for('show_page', page_title=page.title))


@app.route('/sections/<section_id>/delete', methods=["POST"])
def delete_section(section_id):
    """Delete a section"""
    if not g.user:
        flash("Access unauthorized.", "error")
        return redirect("/")
    section = Section.query.get(section_id)
    page_title = section.page_title
    db.session.delete(section)
    db.session.commit()
    return redirect("/page/" + page_title)
#####################################################################
# special links


@app.route('/pages/random')
def random_page():
    """Redirects to a random page"""
    pages = Page.query.filter_by(is_active=True).all()
    page = random.choice(pages)
    if (pages):
        return redirect("/page/" + page.title)
    else:
        return redirect("/pages")


@app.route('/pages/latest')
def latest_page():
    """Redirects to the latest page"""
    pages = Page.query.filter_by(is_active=True).order_by(
        Page.created_at.desc()).all()
    if (pages):
        return redirect("/page/" + pages[0].title)
    else:
        return redirect("/pages")
#####################################################################
# search


@app.route('/search')
def searchWiki():
    """Search for a page"""
    search_term = request.args.get('q')
    pages = Page.query.search(search_term).all()
    section_pages = [section.page for section in (Section.query
                                                  .options(joinedload(Section.page))
                                                  .search(search_term)
                                                  .all())]
    # Use a dict to remove duplicates while preserving order
    pages_dict = {page.id: page for page in pages + section_pages}
    # Convert the dict back to a list
    pages = list(pages_dict.values())
    print(pages)
    print(search_term)
    return render_template('pages/search.html', pages=pages, search_term=search_term)

#####################################################################
# contact


@app.route('/contact')
def contact():
    """Show contact page"""
    return render_template('/pages/contact.html')


#####################################################################
# BIO

@app.route('/users/<int:user_id>')
def show_user(user_id):
    """Show user profile"""
    user = User.query.get_or_404(user_id)
    return render_template('users/user.html', user=user)


@app.route('/users/<int:user_id>/edit', methods=["GET", "POST"])
def edit_user(user_id):
    """Edit user profile"""
    if not g.user:
        flash("Access unauthorized.", "error")
        return redirect("/")
    user = User.query.get_or_404(user_id)
    form = UserEditForm(obj=user)
    if form.validate_on_submit():
        if (user_id != g.user.id):
            flash("Access unauthorized.", "error")
            return redirect("/")
        if (not User.authenticate(user.username, form.confirm_password.data)):
            flash("Incorrect password.", "error")
            return redirect("/users/" + str(user_id) + "/edit")
        user.username = form.username.data
        user.email = form.email.data
        user.character_name = form.character_name.data
        db.session.commit()
        return redirect("/users/" + str(user_id))
    else:
        return render_template("users/edit_user.html", form=form, user=user)


@app.route('/')
def home():
    """Show homepage."""

    return render_template('home.html')

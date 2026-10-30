
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from flask import flash, redirect, render_template, url_for
from werkzeug.security import generate_password_hash

from app.auth import auth
from app.extensions import db
from app.forms.registration import RegistrationForm
from app.models import User

from flask_login import login_user
from werkzeug.security import check_password_hash

from app.forms.login import LoginForm

from flask_login import current_user, login_required, logout_user
from app.forms.logout import LogoutForm


@auth.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()

    if form.validate_on_submit():
        email = form.email.data.strip().lower()

        existing_user = db.session.execute(
            select(User).where(User.email == email)
        ).scalar_one_or_none()

        if existing_user:
            flash("An account with this email already exists.", "error")
            return render_template("auth/register.html", form=form)

        user = User(
            first_name=form.first_name.data.strip(),
            last_name=form.last_name.data.strip(),
            email=email,
            password_hash=generate_password_hash(form.password.data),
        )

        try:
            db.session.add(user)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash("An account with this email already exists.", "error")
            return render_template("auth/register.html", form=form)

        flash("Your account has been created successfully!", "success")
        return redirect(url_for("auth.register"))

    return render_template("auth/register.html", form=form)


@auth.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        email = form.email.data.strip().lower()

        user = db.session.execute(
            select(User).where(User.email == email)
        ).scalar_one_or_none()

        if user and check_password_hash(
            user.password_hash,
            form.password.data,
        ):
            login_user(user)
            flash("You have successfully signed in.", "success")
            return redirect(url_for("auth.dashboard"))

        flash("Invalid email address or password.", "error")

    return render_template("auth/login.html", form=form)


@auth.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    logout_form = LogoutForm()

    return render_template(
        "dashboard.html",
        logout_form=logout_form,
    )


@auth.route("/logout", methods=["POST"])
@login_required
def logout():
    form = LogoutForm()

    if form.validate_on_submit():
        logout_user()
        flash("You have successfully signed out.", "success")
        return redirect(url_for("auth.login"))

    flash("Unable to sign out. Please try again.", "error")
    return redirect(url_for("dashboard"))

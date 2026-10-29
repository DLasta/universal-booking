
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from flask import flash, redirect, render_template, url_for
from werkzeug.security import generate_password_hash

from app.auth import auth
from app.extensions import db
from app.forms.registration import RegistrationForm
from app.models import User


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

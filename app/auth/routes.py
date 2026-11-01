
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from flask import flash, redirect, render_template, url_for
from werkzeug.security import generate_password_hash

from app.auth import auth
from app.extensions import db
from app.forms.registration import RegistrationForm
from app.models import User, Organization
from flask_login import login_user
from werkzeug.security import check_password_hash

from app.forms.login import LoginForm

from flask_login import current_user, login_required, logout_user
from app.forms.logout import LogoutForm
from app.forms.employee import EmployeeForm

from app.forms.service import ServiceForm
from app.models import Service

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

        organization = Organization(
            name=form.organization_name.data.strip(),
            business_type=form.business_type.data,
        )

        user = User(
            first_name=form.first_name.data.strip(),
            last_name=form.last_name.data.strip(),
            email=email,
            password_hash=generate_password_hash(form.password.data),
            organization=organization,
        )

        try:
            db.session.add(organization)
            db.session.add(user)
            db.session.commit()

        except IntegrityError:
            db.session.rollback()
            flash("Registration failed. Please try again.", "error")
            return render_template("auth/register.html", form=form)

        flash("Your account and organization have been created successfully!", "success")
        return redirect(url_for("auth.login"))

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

@auth.route("/employees", methods=["GET", "POST"])
@login_required
def employees():
    if current_user.role != "owner":
        flash("You do not have permission to manage employees.", "error")
        return redirect(url_for("auth.dashboard"))

    if not current_user.organization_id:
        flash("Your account is not connected to an organization.", "error")
        return redirect(url_for("auth.dashboard"))

    form = EmployeeForm()

    if form.validate_on_submit():
        email = form.email.data.strip().lower()

        existing_user = db.session.execute(
            select(User).where(User.email == email)
        ).scalar_one_or_none()

        if existing_user:
            flash("An account with this email already exists.", "error")
            return redirect(url_for("auth.employees"))

        employee = User(
            first_name=form.first_name.data.strip(),
            last_name=form.last_name.data.strip(),
            email=email,
            password_hash=generate_password_hash(form.password.data),
            organization_id=current_user.organization_id,
            role="employee",
        )

        try:
            db.session.add(employee)
            db.session.commit()

            flash("Employee has been added successfully!", "success")
            return redirect(url_for("auth.employees"))

        except IntegrityError:
            db.session.rollback()
            flash("Unable to add employee. Please try again.", "error")

    employees_list = db.session.execute(
        select(User).where(
            User.organization_id == current_user.organization_id,
            User.role == "employee",
        ).order_by(User.first_name)
    ).scalars().all()

    
    return render_template(
        "employees.html",
        form=form,
        employees=employees_list,
        logout_form=LogoutForm(),
    )


@auth.route("/services", methods=["GET", "POST"])
@login_required
def services():
    if current_user.role != "owner":
        flash("You do not have permission to manage services.", "error")
        return redirect(url_for("auth.dashboard"))

    if not current_user.organization_id:
        flash("Your account is not connected to an organization.", "error")
        return redirect(url_for("auth.dashboard"))

    form = ServiceForm()

    if form.validate_on_submit():
        service = Service(
            organization_id=current_user.organization_id,
            name=form.name.data.strip(),
            description=form.description.data.strip() if form.description.data else None,
            duration_minutes=form.duration_minutes.data,
            price=form.price.data,
        )

        db.session.add(service)
        db.session.commit()

        flash("Service added successfully.", "success")
        return redirect(url_for("auth.services"))

    services_list = db.session.execute(
        select(Service)
        .where(Service.organization_id == current_user.organization_id)
        .order_by(Service.name)
    ).scalars().all()

    return render_template(
        "services.html",
        form=form,
        services=services_list,
        logout_form=LogoutForm(),
    )

@auth.route("/services/<int:service_id>/edit", methods=["GET", "POST"])
@login_required
def edit_service(service_id):
    if current_user.role != "owner":
        flash("You do not have permission to edit services.", "error")
        return redirect(url_for("auth.dashboard"))

    if not current_user.organization_id:
        flash("Your account is not connected to an organization.", "error")
        return redirect(url_for("auth.dashboard"))

    service = db.session.execute(
        select(Service).where(
            Service.id == service_id,
            Service.organization_id == current_user.organization_id,
        )
    ).scalar_one_or_none()

    if service is None:
        flash("Service not found.", "error")
        return redirect(url_for("auth.services"))

    form = ServiceForm(obj=service)

    if form.validate_on_submit():
        service.name = form.name.data.strip()
        service.description = (
            form.description.data.strip()
            if form.description.data
            else None
        )
        service.duration_minutes = form.duration_minutes.data
        service.price = form.price.data

        db.session.commit()

        flash("Service updated successfully.", "success")
        return redirect(url_for("auth.services"))

    return render_template(
        "edit_service.html",
        form=form,
        service=service,
        logout_form=LogoutForm(),
    )

@auth.route("/services/<int:service_id>/toggle-status", methods=["POST"])
@login_required
def toggle_service_status(service_id):
    if current_user.role != "owner":
        flash("You do not have permission to manage services.", "error")
        return redirect(url_for("auth.dashboard"))

    if not current_user.organization_id:
        flash("Your account is not connected to an organization.", "error")
        return redirect(url_for("auth.dashboard"))

    service = db.session.execute(
        select(Service).where(
            Service.id == service_id,
            Service.organization_id == current_user.organization_id,
        )
    ).scalar_one_or_none()

    if service is None:
        flash("Service not found.", "error")
        return redirect(url_for("auth.services"))

    service.is_active = not service.is_active
    db.session.commit()

    if service.is_active:
        flash("Service activated successfully.", "success")
    else:
        flash("Service deactivated successfully.", "success")

    return redirect(url_for("auth.services"))
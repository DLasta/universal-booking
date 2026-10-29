
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import (
    DataRequired,
    Email,
    EqualTo,
    Length,
)


class RegistrationForm(FlaskForm):
    first_name = StringField(
        "First name",
        validators=[DataRequired(), Length(max=100)],
    )

    last_name = StringField(
        "Last name",
        validators=[DataRequired(), Length(max=100)],
    )

    email = StringField(
        "Email address",
        validators=[DataRequired(), Email(), Length(max=255)],
    )

    password = PasswordField(
        "Password",
        validators=[DataRequired(), Length(min=12, max=128)],
    )

    confirm_password = PasswordField(
        "Confirm password",
        validators=[
            DataRequired(),
            EqualTo("password", message="Passwords must match."),
        ],
    )

    submit = SubmitField("Create account")

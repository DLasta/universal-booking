
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, DecimalField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange


class ServiceForm(FlaskForm):
    name = StringField(
        "Service Name",
        validators=[
            DataRequired(),
            Length(max=150),
        ],
    )

    description = TextAreaField(
        "Description",
        validators=[
            Length(max=2000),
        ],
    )

    duration_minutes = IntegerField(
        "Duration (minutes)",
        validators=[
            DataRequired(),
            NumberRange(min=5, max=1440),
        ],
    )

    price = DecimalField(
        "Price (€)",
        places=2,
        validators=[
            DataRequired(),
            NumberRange(min=0, max=999999),
        ],
    )

    submit = SubmitField("Add Service")

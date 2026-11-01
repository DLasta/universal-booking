
from datetime import datetime

from flask_login import UserMixin

from app.extensions import db


class Organization(db.Model):
    __tablename__ = "organizations"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(
        db.String(150),
        nullable=False,
    )

    business_type = db.Column(
        db.String(100),
        nullable=True,
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    users = db.relationship(
        "User",
        back_populates="organization",
        lazy=True,
    )

    @property
    def employees(self):
        return [
            user for user in self.users
            if user.role == "employee"
        ]

    def __repr__(self):
        return f"<Organization {self.name}>"


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

   

    organization_id = db.Column(
        db.Integer,
        db.ForeignKey("organizations.id"),
        nullable=True,
        index=True,
    )

    role = db.Column(
            db.String(20),
            nullable=False,
            default="owner",
        )

    email = db.Column(
        db.String(255),
        unique=True,
        nullable=False,
        index=True,
    )

    password_hash = db.Column(
        db.String(255),
        nullable=False,
    )

    first_name = db.Column(
        db.String(100),
        nullable=False,
    )

    last_name = db.Column(
        db.String(100),
        nullable=False,
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    organization = db.relationship(
        "Organization",
        back_populates="users",
    )

    def __repr__(self):
        return f"<User {self.email}>"


class Service(db.Model):
    __tablename__ = "services"

    id = db.Column(db.Integer, primary_key=True)

    organization_id = db.Column(
        db.Integer,
        db.ForeignKey("organizations.id"),
        nullable=False,
        index=True,
    )

    name = db.Column(
        db.String(150),
        nullable=False,
    )

    description = db.Column(
        db.Text,
        nullable=True,
    )

    duration_minutes = db.Column(
        db.Integer,
        nullable=False,
    )

    price = db.Column(
        db.Numeric(10, 2),
        nullable=False,
    )

    is_active = db.Column(
        db.Boolean,
        default=True,
        nullable=False,
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    organization = db.relationship(
        "Organization",
        backref=db.backref("services", lazy=True),
    )

    def __repr__(self):
        return f"<Service {self.name}>"

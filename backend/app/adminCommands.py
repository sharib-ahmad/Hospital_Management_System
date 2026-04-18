import click
from flask.cli import with_appcontext
from .extensions import db
from .models.user import User
from .utils.enum import UserRole

@click.command('create-admin')
@click.argument('username')
@click.argument('email')
@click.argument('password')
@with_appcontext
def create_admin_command(username, email, password):
    """Create a new admin user."""
    # Check if user already exists
    user = User.query.filter((User.username == username) | (User.email == email)).first()
    if user:
        click.echo(f"Error: User with username '{username}' or email '{email}' already exists.")
        return

    # Create new admin user
    admin = User(
        username=username,
        email=email,
        full_name="System Administrator",
        password=password,  # This uses the setter which hashes it
        role=UserRole.ADMIN,
        is_active=True
    )

    try:
        db.session.add(admin)
        db.session.commit()
        click.echo(f"Success: Admin user '{username}' created successfully!")
    except Exception as e:
        db.session.rollback()
        click.echo(f"Error creating admin: {e}")

def register_commands(app):
    """Register Flask CLI commands."""
    app.cli.add_command(create_admin_command)

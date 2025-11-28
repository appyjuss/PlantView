"""
CLI commands for database operations.
Run commands like: flask --app backend.main init-db
"""
import click
from flask.cli import with_appcontext
import os


def register_cli_commands(app):
    """Register CLI commands with the Flask app."""
    
    @app.cli.command('init-db')
    @with_appcontext
    def init_db_command():
        """Initialize the database by running migrations."""
        click.echo('Initializing database...')
        
        from flask_migrate import upgrade
        try:
            upgrade()
            click.echo('✓ Database initialized successfully!')
        except Exception as e:
            click.echo(f'✗ Error initializing database: {e}', err=True)
            raise
    
    @app.cli.command('create-admin')
    @click.option('--email', prompt='Email', help='Admin email address')
    @click.option('--password', prompt=True, hide_input=True, 
                  confirmation_prompt=True, help='Admin password')
    @with_appcontext
    def create_admin_command(email, password):
        """Create an admin user."""
        from werkzeug.security import generate_password_hash
        from backend.core.models import db, User
        from backend.core import auth as core_auth
        
        click.echo(f'Creating admin user: {email}')
        
        # Validate email
        if not core_auth.validate_email(email):
            click.echo('✗ Invalid email format', err=True)
            return
        
        # Validate password
        is_valid, message = core_auth.validate_password_strength(password)
        if not is_valid:
            click.echo(f'✗ {message}', err=True)
            return
        
        # Check if user exists
        existing = User.query.filter_by(email=email.lower()).first()
        if existing:
            click.echo('✗ User already exists', err=True)
            return
        
        try:
            user = User(
                email=email.lower(),
                password_hash=generate_password_hash(password)
            )
            db.session.add(user)
            db.session.commit()
            click.echo(f'✓ Admin user created successfully! (ID: {user.id})')
        except Exception as e:
            db.session.rollback()
            click.echo(f'✗ Error creating admin user: {e}', err=True)
            raise
    
    @app.cli.command('list-users')
    @with_appcontext
    def list_users_command():
        """List all users in the database."""
        from backend.core.models import User
        
        users = User.query.all()
        if not users:
            click.echo('No users found.')
            return
        
        click.echo(f'Total users: {len(users)}\n')
        for user in users:
            click.echo(f'  ID: {user.id}')
            click.echo(f'  Email: {user.email}')
            click.echo(f'  Created: {user.created_at}')
            click.echo(f'  Failed attempts: {user.failed_login_attempts}')
            if user.locked_until:
                click.echo(f'  Locked until: {user.locked_until}')
            click.echo()
    
    @app.cli.command('delete-user')
    @click.option('--email', prompt='Email to delete', help='User email to delete')
    @click.confirmation_option(prompt='Are you sure you want to delete this user?')
    @with_appcontext
    def delete_user_command(email):
        """Delete a user from the database."""
        from backend.core.models import db, User
        
        user = User.query.filter_by(email=email.lower()).first()
        if not user:
            click.echo(f'✗ User {email} not found', err=True)
            return
        
        try:
            db.session.delete(user)
            db.session.commit()
            click.echo(f'✓ User {email} deleted successfully!')
        except Exception as e:
            db.session.rollback()
            click.echo(f'✗ Error deleting user: {e}', err=True)
            raise
    
    @app.cli.command('reset-db')
    @click.confirmation_option(prompt='Are you sure? This will DELETE all data!')
    @with_appcontext
    def reset_db_command():
        """Reset the database (development only)."""
        from backend.core.models import db
        from flask import current_app
        
        if current_app.config['ENV'] == 'production':
            click.echo('✗ Cannot reset database in production!', err=True)
            return
        
        click.echo('Dropping all tables...')
        db.drop_all()
        
        click.echo('Creating tables...')
        db.create_all()
        
        click.echo('✓ Database reset successfully!')
    
    @app.cli.command('migrate-from-json')
    @click.option('--json-file', default='users.json', 
                  help='Path to JSON users file to migrate')
    @with_appcontext
    def migrate_from_json_command(json_file):
        """Migrate users from JSON file to database."""
        import json
        from backend.core.models import db, User
        
        if not os.path.exists(json_file):
            click.echo(f'✗ JSON file not found: {json_file}', err=True)
            return
        
        click.echo(f'Migrating users from {json_file}...')
        
        try:
            with open(json_file, 'r') as f:
                users_data = json.load(f)
            
            migrated = 0
            skipped = 0
            
            for email, user_info in users_data.items():
                # Check if user exists
                existing = User.query.filter_by(email=email.lower()).first()
                if existing:
                    click.echo(f'  Skipping {email} (already exists)')
                    skipped += 1
                    continue
                
                # Create user
                user = User(
                    email=email.lower(),
                    password_hash=user_info.get('password'),
                )
                db.session.add(user)
                migrated += 1
            
            db.session.commit()
            click.echo(f'✓ Migration complete! Migrated: {migrated}, Skipped: {skipped}')
            
        except json.JSONDecodeError:
            click.echo(f'✗ Invalid JSON in file', err=True)
            raise
        except Exception as e:
            db.session.rollback()
            click.echo(f'✗ Error during migration: {e}', err=True)
            raise
    
    @app.cli.command('db-status')
    @with_appcontext
    def db_status_command():
        """Check database connection and status."""
        from backend.core.models import db, User
        
        try:
            # Try to query users
            count = User.query.count()
            click.echo(f'✓ Database connection successful!')
            click.echo(f'  Users in database: {count}')
            click.echo(f'  Database URL: {db.engine.url}')
        except Exception as e:
            click.echo(f'✗ Database connection failed: {e}', err=True)

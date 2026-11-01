import click

from flask import Flask
from flask_migrate import Migrate
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData

class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSON_SORT_KEYS = False

class DevConfig(Config):
    SQLALCHEMY_DATABASE_URI = "sqlite:///app.db"
    DEBUG = True

class TestConfig(Config):
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    TESTING = True

config_dict = {
    "dev": DevConfig,
    "test": TestConfig,
}

metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

def create_app(env="dev"):
    app = Flask(__name__)
    app.config.from_object(config_dict[env])
    app.json.compact = False

    db.init_app(app)
    migrate.init_app(app, db)

    # Register routes on every app, including apps created by tests or Flask.
    from resources import Books

    api = Api(app)
    api.add_resource(Books, '/books', endpoint='books')

    @app.cli.command('init-db')
    def init_db():
        """Create missing tables without deleting existing records."""
        db.create_all()
        click.echo('Database initialized.')

    return app

db = SQLAlchemy(metadata=metadata)
migrate = Migrate()

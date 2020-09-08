from flask import Flask
import warnings


warnings.simplefilter("ignore")

def create_app():
    """Initialize the core application."""
    app = Flask(__name__, instance_relative_config=False)

    with app.app_context():
        # Include our Routes
        from . import routes

        return app

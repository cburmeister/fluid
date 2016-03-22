"""
Browse your local movies with IMDB data and stream them to a Chromecast.
"""
from flask import Flask
from flask_bower import Bower
from routes import root
import argparse
import logging
import os
import sys

reload(sys)
sys.setdefaultencoding("utf-8")


def init_app():
    """Returns an instance of the application."""
    app = Flask(__name__)
    app.config.update({
        'CHROMECAST_IP': os.environ['CHROMECAST_IP'],
        'MEDIA_PATH': os.environ['MEDIA_PATH'],
        'SECRET_KEY': os.environ['SECRET_KEY'],
        'LOG_PATH': os.environ.get('LOG_PATH', 'fluid.log'),
    })
    init_blueprints(app)
    init_extensions(app)
    init_logging(app)
    return app


def init_blueprints(app):
    """Registers blueprints with the application."""
    app.register_blueprint(root)


def init_extensions(app):
    """Registers extensions with the application."""
    Bower(app)


def init_logging(app):
    """Setup logging for the application."""
    logger = logging.getLogger()

    # Describe format of logs
    log_format = str(
        '%(asctime)s:%(levelname)s:%(module)s.py:%(lineno)d - %(message)s'
    )

    # Setup the StreamHandler to log to stderr
    logging.basicConfig(level=logging.DEBUG, format=log_format)

    if app.debug:  # Logging to stderr is sufficient when debugging
        return

    # Setup a FileHandler to log to a configurable path
    file_handler = logging.FileHandler(app.config['LOG_PATH'])
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(log_format))
    logger.addHandler(file_handler)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--debug', action='store_true', default=False)
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', default='5000', type=int)
    args = parser.parse_args()

    app = init_app()
    app.run(host=args.host, port=args.port, debug=args.debug)

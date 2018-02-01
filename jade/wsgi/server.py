import os

import flask_swaggerui

from . import responses
from .. import errors
from jade.centralauth import CentralAuth
# TODO:
#from jade.state_stores import StateStore
from jade.trusted_clients import TrustedClients


def configure(config):

    from flask import Blueprint, Flask

    from . import routes

    directory = os.path.dirname(os.path.realpath(__file__))

    app = Flask(__name__,
                static_url_path="/BASE_STATIC",
                template_folder=os.path.join(directory, 'templates'))

    app.config['APPLICATION_ROOT'] = config['jade']['wsgi']['application_root']
    app.url_map.strict_slashes = False
    # Configure routes
    bp = Blueprint('jade', __name__,
                   static_folder=os.path.join(directory, 'static'),
                   url_prefix=config['jade']['wsgi']['url_prefix'])

    trusted_clients = TrustedClients.from_config(config)
    centralauth = CentralAuth.from_config(config)
    # state_store = StateStore.from_config(config)
    state_store = None

    bp = routes.configure(
        config, bp, trusted_clients, centralauth, state_store)
    app.register_blueprint(bp)

    # Configure swagger-ui routes
    swagger_bp = flask_swaggerui.build_static_blueprint(
        'jade-swaggerui', __name__,
        url_prefix=config['jade']['wsgi']['url_prefix'])
    app.register_blueprint(swagger_bp)

    @app.errorhandler(errors.RequestError)
    def handle_request_error(e):
        responses.format_request_error(e)

    @app.errorhandler(Exception)
    def handle_unknown_error(e):
        responses.format_unknown_error(e)
    return app

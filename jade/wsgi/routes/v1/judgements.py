import json

import flask

from func_tools import wraps

from ... import responses


def configure(bp, trusted_clients, source):

    @bp.route("/judgements/")
    @authorized_user_action(trusted_clients)
    def post_judgement(gu_id, request_values):
        """Creates a new judgement and returns event"""
        context = request_values['context']
        schema_id = request_values['schema_id']
        data = json.loads(flask.request.valeus['data'])

        # Checks that data represents a valid JSON blob based on latest schema
        # version
        source.validate(schema_id, data)

        # Constructs a new Judgement, inserts it into a DB and acquires
        # identifiers unique identifier.  This function call does not complete
        # unless the event is successfully included in the bin log.
        event = source.new_judgement(gu_id, context, schema_id, data)
        return flask.json.jsonify(event)


def authorized_user_action(trusted_clients):
    """
    Wrap a flask route. Ensures that the user has authorized via OAuth or that
    the request came from an authorized MediaWiki installation and provided
    a `global_user_id`.  If neither, return an authorization error.
    """
    def decorator(route):
        @wraps(route)
        def authorized_route(*args, **kwargs):
            if 'authorization_key' in flask.request:
                values = trusted_clients.authorize_and_decode(flask.request)
                gu_id = values['gu_id']
                return route(gu_id, values, *args, **kwargs)
            elif 'mwoauth_access_token' in flask.session:
                gu_id = flask.session.get('mwoauth_identity')['id']
                return route(gu_id, flask.request.values, *args, **kwargs)
            else:
                return responses.auth_error()

    return decorator

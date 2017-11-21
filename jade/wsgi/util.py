from functools import wraps

import flask

from . import responses
from .. import errors


def authorized_user_action(config, trusted_clients, centralauth, rights_group):
    """
    Wrap a flask route and performs checks that a user is authorized and has
    the rights to perform a specific action.  Authorization is confirmed via
    OAuth or via a trusted MediaWiki installation and provided
    a `global_user_id`.  If neither, return an authorization error.
    """
    def decorator(route):
        @wraps(route)
        def authorized_route(*args, **kwargs):
            if 'authorization_key' in flask.request:
                values = trusted_clients.authorize_and_decode(flask.request)
                gu_id = values['gu_id']
            elif 'mwoauth_access_token' in flask.session:
                values = flask.request.values
                gu_id = flask.session.get('mwoauth_identity')['id']
            else:
                return responses.auth_error()

            requirements = config['actions']['rights'][rights_group]
            try:
                centralauth.check_user_rights(gu_id, requirements)
            except errors.UserRightsError as e:
                return responses.rights_error(e)
            else:
                return route(gu_id, values, *args, **kwargs)

    return decorator


def execute_and_log_or_error(state, proto_event):
    try:
        event = state.events.execute_and_log(proto_event)
    except RuntimeError as e:
        return responses.event_execution_error(e, proto_event)

    return flask.json.jsonify(event)

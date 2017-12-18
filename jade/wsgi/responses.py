import flask

from .. import errors


def format_request_error(e):
    return e.HTTP_CODE, flask.jsonify(e.format_json())


def format_unknown_error(e):
    e = errors.UnknownError(e)
    return e.HTTP_CODE, flask.jsonify(e.format_json())

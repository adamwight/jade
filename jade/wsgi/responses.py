import flask

from .. import errors


def error(e):
    if not isinstance(e, errors.RequestError):
        e = error.UnknownError(e)
    return e.HTTP_CODE, flask.jsonify(e.format_json())

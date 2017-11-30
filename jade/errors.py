import sys
import traceback


class RequestError(RuntimeError):
    "An error occured inside of JADE while processing a request"
    TYPE = None
    SUBTYPE = None
    HTTP_CODE = 500

    def format_detail(self):
        return None

    def format_json(self):
        return {'type': self.TYPE, 'subtype': self.SUBTYPE,
                'message': self.__class__.__doc__,
                'detail': self.format_detail()}


class UnknownError(RequestError):
    "An unknown error occured inside of JADE while processing a request."
    TYPE = "unknown"

    def __init__(self, e):
        super().__init__()
        self.e = e

    def format_detail(self):
        doc = {'exception': str(self.e)}
        if __debug__:
            doc['traceback'] = get_tb()
        return doc


###############################################################################
class EventExecutionError(RequestError):
    "The execution of a proto-event failed."
    TYPE = "event_execution"

    def __init__(self, proto_event, e):
        super().__init__()
        self.proto_event = proto_event
        self.e = e

    def format_detail(self):
        doc = {'proto_event': self.proto_event,
               'exception': str(self.e)}
        if __debug__:
            doc['traceback'] = get_tb()
        return doc


###############################################################################
class MalformedRequestError(RequestError):
    "Something was wrong with the user's request."
    TYPE = "malformed_request"
    HTTP_CODE = 400


class ParameterError(MalformedRequestError):
    "There was something wrong with a parameter in the user's request."
    SUBTYPE = "parameter"

    def __init__(self, parameter, expected, instead):
        super().__init__()
        self.expected = expected
        self.instead = instead

    def format_detail(self):
        return {'parameter': self.parameter,
                'expected': self.expected,
                'instead': self.instead}


class MissingParameterError(MalformedRequestError):
    "A parameter was missing from a user's request."
    SUBTYPE = "missing_parameter"

    def __init__(self, parameter):
        super().__init__()
        self.parameter = parameter

    def format_detail(self):
        return {'parameter': self.parameter}


###############################################################################
class UserPermissionError(RequestError):
    "An error occurred while checking user permission."
    TYPE = "user_permission"
    HTTP_CODE = 403


class UserBlockedError(UserPermissionError):
    "This action cannot be performed because the user is blocked."
    SUBTYPE = "user_blocked"
    HTTP_CODE = 403

    def __init__(self, gu_id, context, expiry, reason):
        super().__init__()
        self.gu_id = gu_id
        self.context = context
        self.expiry = expiry
        self.reason = reason

    def format_detail(self):
        return {'gu_id': self.gu_id,
                'context': self.context,
                'expiry': self.expiry,
                'reason': self.reason}


class UserRightsError(UserPermissionError):
    "This action cannot be performed because the user lacks necessary rights."
    SUBTYPE = "user_rights"

    def __init__(self, gu_id, context, required, user_groups):
        super().__init__()
        self.gu_id = gu_id
        self.context = context
        self.required = required
        self.user_groups = user_groups

    def format_detail(self):
        return {'gu_id': self.gu_id,
                'context': self.context,
                'required': self.required,
                'user_groups': self.user_groups}


class AuthenticationError(UserPermissionError):
    "This action cannot be performed because the user is not authenticated."
    SUBTYPE = "authentication"
    HTTP_CODE = 401


class UserExistenceError(UserPermissionError):
    "This action cannot be performed because the user doesn't exist."
    SUBTYPE = "user_existence"


class TrustedClientVerificationError(UserPermissionError):
    "This action cannot be performed because the client cannot be validated."
    SUBTYPE = "trusted_client_verification"
    HTTP_CODE = 401

    def __init__(self, auth_key, exception):
        super().__init__()
        self.auth_key = auth_key
        self.exception = exception

    def format_details(self):
        doc = {'auth_key': self.auth_key,
               'exception': str(self.exception)}
        if __debug__:
            doc['traceback'] = get_tb()
        return doc


def get_tb():
    ex_type, ex, tb = sys.exc_info()
    return list(traceback.extract_tb(tb))

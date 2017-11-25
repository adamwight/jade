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
        self.e = e

    def format_detail(self):
        doc = {'exception': str(self.e)}
        if __debug__:
            ex_type, ex, tb = sys.exc_info()
            return {'traceback': list(traceback.extract_tb(tb))}

        return doc


###############################################################################
class EventExecutionError(RequestError):
    "The execution of a proto-event failed."
    TYPE = "event_execution_error"

    def __init__(self, proto_event, e):
        self.proto_event = proto_event
        self.e = e

    def format_detail(self):
        doc = {'proto_event': self.proto_event,
               'exception': str(self.e)}
        if __debug__:
            ex_type, ex, tb = sys.exc_info()
            doc['traceback'] = list(traceback.extract_tb(tb))

        return doc


###############################################################################
class MalformedRequestError(RequestError):
    "Something was wrong with the user's request."
    TYPE = "malformed_request"
    HTTP_CODE = 400


class ParameterError(MalformedRequestError):
    "There was something wrong with a parameter in the user's request."
    SUBTYPE = "parameter_error"

    def __init__(self, parameter, expected, instead):
        self.parameter = parameter
        self.expected = expected
        self.instead = instead

    def format_detail(self):
        return {'parameter': self.parameter,
                'expected': self.expected,
                'instead': self.instead}


class MissingParameterError(MalformedRequestError):
    "A parameter was missing from a user's request."
    SUBTYPE = "missing_parameter_error"

    def __init__(self, parameter):
        self.parameter = parameter

    def format_detail(self):
        return {'parameter': self.parameter}


###############################################################################
class UserPermissionError(RequestError):
    "An error occurred while checking user permission."
    TYPE = "user_permission_error"
    HTTP_CODE = 403


class UserBlockedError(UserPermissionError):
    "This action cannot be performed because the user is blocked."
    SUBTYPE = "user_blocked_error"
    HTTP_CODE = 403

    def __init__(self, gu_id, context, expiry, reason):
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
    SUBTYPE = "user_rights_error"

    def __init__(self, gu_id, context, required, user_groups):
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
    SUBTYPE = "authentication_error"
    HTTP_CODE = 401


class UserExistenceError(UserPermissionError):
    "This action cannot be performed because the user doesn't exist."
    SUBTYPE = "user_existence_error"


class TrustedClientVerificationError(UserPermissionError):
    "This action cannot be performed because the client cannot be validated."
    SUBTYPE = "trusted_client_verification_error"
    HTTP_CODE = 401

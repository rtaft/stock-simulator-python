
class HttpError(Exception):
    """
    Generic Exception to be used for Http Errors
    """
    def __init__(self, response_code, body=None):
        """
        Inits the error
        :param response_code: The HTTP Response Code
        :param body: Text to be supplied with this error
        """
        Exception.__init__(self)
        self.body = body
        self.response_code = response_code


class MalformedRequest(HttpError):
    """
    400 Malformed Request
    """
    def __init__(self, body='Malformed Request'):
        """
        Inits error
        :param body: Text to be supplied with this error
        """
        HttpError.__init__(self, 400, body)


class Unauthorized(HttpError):
    """
    401 Unauthorized
    """
    def __init__(self, body='Unauthorized'):
        """
        Inits error
        :param body: Text to be supplied with this error
        """
        HttpError.__init__(self, 401, body)


class PermissionDenied(HttpError):
    """
    403 Permission Denied
    """
    def __init__(self, body='Permission Denied'):
        """
        Inits error
        :param body: Text to be supplied with this error
        """
        HttpError.__init__(self, 403, body)


class NotFound(HttpError):
    """
    404 Not Found
    """
    def __init__(self, body='Not Found'):
        """
        Inits error
        :param body: Text to be supplied with this error
        """
        HttpError.__init__(self, 404, body)


class SessionExpired(HttpError):
    """
    408 Session Expired
    """
    def __init__(self, body='Session Expired'):
        """
        Inits error
        :param body: Text to be supplied with this error
        """
        HttpError.__init__(self, 408, body)
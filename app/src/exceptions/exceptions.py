from typing import AnyStr

class HTTPException(Exception):
    """Baseclass for all HTTP exceptions.  This exception can be called as WSGI
    application to render a default error page or you can catch the subclasses
    of it independently and render nicer error messages.
    """

    message: str
    error_code: int

    def __init__(self, message=None, error_code=None):
        super(HTTPException, self).__init__()
        self.message = message
        self.error_code = error_code

    def handle_error(self):
        from flask import jsonify
        message = [str(x) for x in self.args]
        response = {
            'class': self.__class__.__name__,
            'message': self.message,
            'code': self.error_code or 'unknown'
        }

        return jsonify(response)

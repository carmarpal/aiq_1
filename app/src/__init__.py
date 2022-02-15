from flask import Blueprint
from flask_restplus import Api
from app.src.exceptions.exceptions import HTTPException

# A way to organize applications in Flask
blueprint = Blueprint('api', __name__)

@blueprint.app_errorhandler(HTTPException)
def handle_error(error):
    return error.handle_error()

# Generic error handler for APIException
def handle_error(error):
    return error.handle_error()


# Add namespaces to swagger
api = Api(blueprint)

# TODO Change
from .controller.namespace_api import ns

api.add_namespace(ns)

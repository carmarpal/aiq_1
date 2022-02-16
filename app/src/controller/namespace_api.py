import logging
import injector
from datetime import datetime
from flask import request, jsonify
from flask_accepts import responds, accepts
from flask_restplus import Resource, Namespace
from marshmallow import ValidationError

from app.src.model.model import RequestSchema, ResponseSchema
from app.src.service.plantsservice import PlantsService

# Namespace of resource f.e in this case /default, all the routes under this ns would have /default as prefix
ns = Namespace('', description='API')
log = logging.getLogger(__name__)


@ns.route('/check', methods=['GET'])
class server_check(Resource):
    def get(self):
        now = datetime.now().strftime('%d/%b/%Y - %H:%M:%S.%f\n')
        return "OK!" + now.upper()

# Blank route, so the final uri is /default
@ns.route('/service')
class DefaultApi(Resource):
    PlantsService: PlantsService

    @injector.inject
    def __init__(self, plants: PlantsService, **kwargs):
        super().__init__(**kwargs)
        self.plants = plants

    @accepts(api=ns, schema=RequestSchema())  # Swagger representation fixed in next version of flask_accepts(0.15.5)
    #@responds(schema=ResponseSchema, validate=True, api=ns, status_code=200)
    def post(self):
        debug = request.args.get('debug', default=False, type=bool)

        N, state = request.parsed_obj
        response = self.plants.top_n_plants(N=N, state=state)

        return response
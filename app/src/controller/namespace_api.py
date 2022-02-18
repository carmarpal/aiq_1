import logging
import injector
from datetime import datetime
from flask import request
from flask_accepts import accepts
from flask_restplus import Resource, Namespace

from app.src.model.model import RequestSchema
from app.src.service.plantsservice import PlantsService

# Namespace of resource
ns = Namespace('', description='API')

logging.basicConfig(
    level=logging.INFO,
    format="(asctime)s: %(name)s %(levelname)s %(message)s",
    datefmt="%m-%d %H: %M"
)

# health GET endpoint
@ns.route('/check', methods=['GET'])
class server_check(Resource):
    def get(self):
        now = datetime.now().strftime('%d/%b/%Y - %H:%M:%S.%f\n')
        return "OK!" + now.upper()

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
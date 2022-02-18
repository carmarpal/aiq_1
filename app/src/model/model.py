from dataclasses import dataclass
from marshmallow import fields, Schema, post_load, INCLUDE


# Request marshmallow expected
class RequestSchema(Schema):
    # Allow unknown fields
    class Meta:
        unknown = INCLUDE

    # Schema
    N = fields.Integer(required=True)
    State = fields.String(required=False)
    @post_load
    def make(self, data, **kwargs):
        N = data['N']
        State = data['State'] if 'State' in data.keys() else None
        return N, State

from parse_rest.connection import api_root
from parse_rest.datatypes import ParseResource

class Config(ParseResource):
    @classmethod
    def endpoint_root(cls):
        return '/'.join([api_root(), 'config'])

    @classmethod
    def get(cls):
        return cls.GET('').get('params')

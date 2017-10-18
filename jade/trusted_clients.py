import jwt
from werkzeug.datastructures import MultiDict

HASH_ALGORITHM = "HS256"


class AuthorizedClients:

    def __init__(self, key_secrets):
        self.key_secrets = dict(key_secrets)

    def authorize_and_decode(self, request):
        auth_key = request.values['auth_key']
        encoded_values = request.values['encoded_values']

        return json2multidict(jwt.decode(
            encoded_values, self.key_secrets[auth_key],
            algorithms=[HASH_ALGORITHM]))

    @classmethod
    def from_config(cls, config):
        return cls(config['authorized_clients']['key_secrets'])


def json2multidict(doc):
    return MultiDict(json2items(doc))


def json2items(doc):
    for key, value_or_list in doc.items():
        if isinstance(value_or_list, list):
            for val in value_or_list:
                yield key, val
        else:
            yield key, value_or_list

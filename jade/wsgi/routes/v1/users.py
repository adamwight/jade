import json

import flask

from ... import util
from .... import errors, types


def configure(config, bp, trusted_clients, centralauth, state):
    raise NotImplementedError()

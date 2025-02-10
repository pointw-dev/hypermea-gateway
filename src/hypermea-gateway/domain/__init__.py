"""
Defines the resources that comprise the hypermea-gateway domain.
"""
from . import _settings
from . import gateway_registrations
from ._common import OBJECT_ID_REGEX


DOMAIN_DEFINITIONS = {
    '_settings': _settings.DEFINITION,
    'gateway_registrations': gateway_registrations.DEFINITION
}


DOMAIN_RELATIONS = {
}


DOMAIN = {**DOMAIN_DEFINITIONS, **DOMAIN_RELATIONS}

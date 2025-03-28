"""
Defines the gateway_registrations resource.
"""
from domain._common import COMMON_FIELDS

SCHEMA = {
    "name": {"type": "string", "required": True, "empty": False, "unique": True},
    "description": {"type": "string"},
    "baseUrl": {"type": "string"},
    "rels": {
        "type": "dict",
        "keysrules": {
            "type": "string"
        },  # TODO: conforms to link_rel constraints [RFC8288]
        "valuesrules": {
            "type": "dict",
            "schema": {
                "href": {
                    "type": "string"
                },  # TODO: conforms to URI constraints [RFC3986]
                "_note": {"type": "string"},
                "title": {"type": "string"},
                "_prompt": {"type": "string"},
                "templated": {
                    'type': 'boolean',
                    'required': False
                }
            },
        },
    },
}

SCHEMA.update(COMMON_FIELDS)

DEFINITION = {
    "schema": SCHEMA,
    "datasource": {"projection": {"_role": 0, "_acl": 0}},
    "additional_lookup": {
        "url": 'regex("[\w]+")',  # pylint: disable=anomalous-backslash-in-string
        "field": "name",
    },
    "item_methods": ['GET', 'PUT', 'DELETE']
}

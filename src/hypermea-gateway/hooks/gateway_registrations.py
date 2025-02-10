"""
hooks.gateway_registrations
This module defines functions to add link relations to gateway_registrations.
"""
import json
from hypermea.core.logging import trace


@trace
def add_hooks(app):
    """Wire up the hooks for gateway_registrations."""
    app.on_fetched_item_gateway_registrations += _add_links_to_gateway_registration
    app.on_fetched_resource_gateway_registrations += _add_links_to_gateway_registrations_collection
    app.on_post_POST_gateway_registrations += _post_gateway_registrations
    app.on_pre_POST_gateway_registrations += _before_insert_gateway_registrations


@trace
def _before_insert_gateway_registrations(request):
    data = json.loads(request.get_data())
    data['rels'].pop('self')
    request._cached_data = json.dumps(data).encode('utf-8')


@trace
def _post_gateway_registrations(request, payload):
    if payload.status_code == 201:
        j = json.loads(payload.data)
        if '_items' in j:
            for gateway_registration in j['_items']:
                _add_links_to_gateway_registration(gateway_registration)
        else:
            _add_links_to_gateway_registration(j)
        payload.data = json.dumps(j)


@trace
def _add_links_to_gateway_registrations_collection(gateway_registrations_collection):
    for gateway_registration in gateway_registrations_collection['_items']:
        _add_links_to_gateway_registration(gateway_registration)


@trace
def _add_links_to_gateway_registration(gateway_registration):
    gateway_registration['_links']['self'] = {
        'href': f"/gateway_registrations/{gateway_registration['_id']}",
        'title': 'gateway_registration'
    }

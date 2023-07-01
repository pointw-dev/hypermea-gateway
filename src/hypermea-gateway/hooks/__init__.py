import logging
import json
import re
from utils import echo_message, get_db, get_my_base_url
import hooks._error_handlers
import hooks._settings
import hooks._logs
from log_trace.decorators import trace
from configuration import SETTINGS
import hooks.registrations
import hashlib


LOG = logging.getLogger('hooks')


class EtagException(Exception):
    def __init__(self, status_code):
        self.status_code = status_code


@trace
def add_hooks(app):
    app.on_post_GET += _fix_links
    app.on_post_PATCH += _fix_links
    app.on_post_POST += _tidy_post_links

    if SETTINGS.has_enabled('HY_ADD_ECHO'):
        @app.route('/_echo', methods=['PUT'])
        def _echo_message():
            return echo_message()

    hooks._error_handlers.add_hooks(app)
    hooks._settings.add_hooks(app)
    hooks._logs.add_hooks(app)
    hooks.registrations.add_hooks(app)


@trace
def _tidy_post_links(resource, request, payload):
    if payload.status_code == 201:
        document = json.loads(payload.data)
        if '_items' in document:
            for item in document['_items']:
                _remove_unnecessary_links(links=item.get('_links', {}))
        else:
            _remove_unnecessary_links(links=document.get('_links', {}))

        if 'pretty' in request.args:
            payload.data = json.dumps(document, indent=4)
        else:
            payload.data = json.dumps(document)


@trace
def _fix_links(resource, request, payload):
    if payload.status_code in [200, 201]:
        document = json.loads(payload.data)

        if resource is None:
            try:
                document = _handle_schema_request(document, payload, request)
            except EtagException as ex:
                payload.status_code = ex.status_code
                payload.data = b''
                return
        else:
            if '_items' in document:
                for item in document['_items']:
                    _process_item_links(links=item.get('_links', {}))
            else:
                _add_parent_link(links=document.get('_links', {}), resource=resource)
            _process_item_links(links=document.get('_links', {}))

        payload.data = json.dumps(document, indent=4 if 'pretty' in request.args else None)


@trace
def _handle_schema_request(document, payload, request):
    document, etag = _rewrite_schema_links(document)
    payload.headers.add_header('Etag', etag)
    document['_etag'] = etag

    if_none_match_header = request.headers.get('if-none-match', '')
    if_match_header = request.headers.get('if-match', '')

    if if_none_match_header == '*' or etag in if_none_match_header:
        raise EtagException(304)  # Not modified
    if if_match_header and etag not in if_match_header:
        raise EtagException(412)  # Precondition failed

    return document


@trace
def _process_item_links(links):
    if not links:
        return

    _remove_unnecessary_links(links)

    for link in links.values():
        _add_missing_slashes(link)
        _insert_base_url(link)
        _remove_regex_from_href(link)


@trace
def _rewrite_schema_links(document):
    base_url = get_my_base_url()
    
    if '_links' in document and 'child' in document['_links'] and len(document['_links']) == 1:
        old = document['_links']['child']
        del document['_links']['child']
        new_links = _create_new_schema_links(base_url, old)
        document['_links'] = new_links
    
    document = _create_gateway_links(document)
    return document, hashlib.md5(json.dumps(document['_links']).encode('utf-8')).hexdigest()

@trace
def _create_new_schema_links(base_url, old_links):
    new_links = {
        'self': {'href': f'{base_url}/', 'title': 'hypermea-gateway root'},
        'logging': {'href': f'{base_url}/_logging', 'title': 'logging'}
    }

    for link in old_links:
        if '<' not in link['href'] and not link['title'] == '_schema':
            rel = link['title'][1:] if link['title'].startswith('_') else link['title']
            link['href'] = f'{base_url}/{link["href"]}'
            new_links[rel] = link

    return new_links


@trace
def _remove_unnecessary_links(links):
    if not links:
        return

    if 'related' in links:
        del links['related']


@trace
def _add_missing_slashes(link):
    href = link.get('href')
    if href and not (href.startswith('/') or href.startswith('http://') or href.startswith('https://')):
        link['href'] = '/' + href


@trace
def _insert_base_url(link):
    base_url = get_my_base_url()
    if link['href'].startswith('/'):
        link['href'] = f'{base_url}{link["href"]}'


@trace
def _remove_regex_from_href(link):
    # TODO: this is needed due to a bug in Eve - fix that bug!
    if '<regex' in link['href']:
        link['href'] = re.sub('\/\<regex.*?\>', '', link['href'])


@trace
def _add_parent_link(links, resource):
    if not links or 'collection' not in links:
        return

    links['parent'] = {
        'href': links['collection']['href'],
        'title': resource
    }


@trace
def _create_gateway_links(j):
    db = get_db()
    registration_col = db["registrations"]
    curies = []
    all_links = dict()
    for record in registration_col.find():
        for key, value in record["rels"].items():
            if registration_col.count_documents({
                "$and": [
                    {f"rels.{key}": {'$exists': 1}},
                    {'name': {"$ne": record["name"]}}
                ]
            }) or j["_links"].get(f"{key}") is not None:
                all_links[record["name"] + ":" + key] = record["rels"][key]
            else:
                all_links[key] = record["rels"][key]
            curie_instance = dict()
            curie_instance["name"] = record["name"]
            curie_instance["href"] = (
                SETTINGS.get("GW_CURIES_NAMESPACE_URI", "")
                + f'/{record["name"]}/relations/{"{rel}"}'
            )
            curie_instance["templated"] = True
            if curie_instance not in curies:
                curies.append(curie_instance)
    j = {"_links": all_links | j["_links"]}
    if curies:
        j["_links"]["curies"] = curies
    return j

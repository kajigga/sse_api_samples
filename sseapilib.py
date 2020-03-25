#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests
import os

# Define these in ENV variables
API_HOST = os.getenv('API_HOST', 'https://sse-hostname-here')
API_USERNAME = os.getenv('API_USERNAME', 'root')
# API_PASSWORD = "some-secure-password"
API_PASSWORD = os.getenv('API_PASSWORD')

# --------------------------------------------------------------------------

API_URL = "{}/rpc".format(API_HOST)

CTX = {}


def make_session():
    """TODO: Docstring for make_session.
    :returns: TODO

    """
    if not CTX.get('session'):
        session = requests.Session()
        session.auth = (API_USERNAME, API_PASSWORD)

        # uncomment if your sse server is not using a valid TLS Certificate
        # session.verify = False

        r = session.get('{}/account/login'.format(API_HOST))

        # Step two, use xsrf token in the header to make the API call
        session.headers.update({
            'X-Xsrftoken': r.headers['X-Xsrftoken'],
        })
        CTX['session'] = session
    return CTX['session']


def api(resource_method, get_raw=False, **payload):
    resource, method = resource_method.split('.')
    # get envs
    CMD_TO_RUN = {
      "resource": resource,
      "method": method
    }
    if payload:
        CMD_TO_RUN['kwarg'] = payload

    # pprint(CMD_TO_RUN)

    session = make_session()

    res = session.post(API_URL, json=CMD_TO_RUN).json()

    if get_raw:
        return res
    return res.get('ret')

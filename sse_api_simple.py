#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests
import os
from pprint import pprint

# Define these in ENV variables
API_HOST = os.getenv('API_HOST', 'https://sse-hostname-here')
API_USERNAME = os.getenv('API_USERNAME', 'root')
# API_PASSWORD = "some-secure-password"
API_PASSWORD = os.getenv('API_PASSWORD')
TGT_UUID = '7f93b928-388b-11e6-b133-346895ecb8f3'

# Step one: authenticate and save xsrf token

session = requests.Session()
session.auth = (API_USERNAME, API_PASSWORD)

# uncomment if your sse server is not using a valid TLS Certificate
# session.verify = False

r = session.get('{}/account/login'.format(API_HOST))

# Step two, use xsrf token in the header to make the API call
session.headers.update({
    'X-Xsrftoken': r.headers['X-Xsrftoken'],
})

CMD_TO_RUN = {
  "resource": "tgt",
  "method": "get_target_group",
  "kwarg": {
  }
}

resp = session.post('{}/rpc'.format(API_HOST), json=CMD_TO_RUN)

for tg in resp.json()['ret']['results']:
    print('{}: {}'.format(tg['name'], tg['uuid']))

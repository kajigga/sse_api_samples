#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from pprint import pprint
from sseapi import SSEAPI_PY

# Define these in ENV variables
API_HOST = os.getenv('API_HOST', 'https://sse-hostname-here')
API_USERNAME = os.getenv('API_USERNAME', 'root')
# API_PASSWORD = "some-secure-password"
API_PASSWORD = os.getenv('API_PASSWORD')

# Step one: authenticate and save xsrf token

client = SSEAPI_PY(API_HOST, username=API_USERNAME, password=API_PASSWORD)

# Get a list of target groups
resp = client.tgt.get_target_group()

for tgt in resp['ret']['results']:
    print('{}: {}'.format(tgt['name'], tgt['uuid']))


# Run a cmd on some minions
# This will run on multiple masters and be controlled with SSE's RBAC


# salt \* test.ping
resp = client.cmd.route_cmd(cmd='local',
                            fun='test.ping',
                            tgt={
                                '*': {  # <-- A start here indicates all masters
                                    'tgt': '*',  # <-- target pattern
                                    'tgt_type': 'glob'
                                    }
                                })

pprint(resp)

# salt centos1* cmd.run "ls /etc"
resp = client.cmd.route_cmd(cmd='local',
                            fun='cmd.run',
                            arg={
                                'arg': ["ls /etc"]
                            },
                            tgt={
                                '*': {  # <-- A start here indicates all masters
                                    'tgt': 'centos1*',  # <-- target pattern
                                    'tgt_type': 'glob'
                                    }
                                })

# All cmd executions are asynchronous via the SSE API.
# What you will get back is something that looks like this.
pprint(resp)
'''
{'error': None,
 'ret': '20200323221245162594',
 'riq': 140398180249784,
 'warnings': []}
'''

# You can fetch the statsus of a cmd like this after you have the jid. The jid
# will take a few moments to generate so it is not immediately available to
# query for the status.

resp = client.cmd.get_cmd_status(jids=['20200323221245162594'])

pprint(resp)

# Run a predifined job

# The job_uuid comes from SSE. All of the other parameters are defined in SSE
resp = client.cmd.route_cmd(job_uuid='5917bdf1-c3a7-486a-b374-9d6210d74e19')

pprint(resp)

# Same thing but also pass in a target UUID from SSE
resp = client.cmd.route_cmd(job_uuid='5917bdf1-c3a7-486a-b374-9d6210d74e19',
                            tgt_uuid='8f274017-e77e-4a70-8d25-d9c99d6219d9')

pprint(resp)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import pathlib
from sseapilib import api

# directory where the files will be exported, Must end with /
export_path = '/tmp/sseexport/'

# get list of files for current env
envs = api('fs.get_envs')

for env in envs:
    # ignore sse env
    if env == 'sse':
        continue
    files = api('fs.get_env', saltenv=env)
    # iterate over those files
    for thefile in files:
        thefile['local_path'] = os.path.join(export_path,
                                             thefile['saltenv'],
                                             thefile['path'][1:]  # remove leading slash
                                             )

        pathlib.Path(os.path.dirname(thefile['local_path'])).mkdir(parents=True,
                                                                   exist_ok=True)

        # write that file
        dasfile = api('fs.get_file', file_uuid=thefile['uuid'])

        with open(thefile['local_path'], 'w') as outfile:
            outfile.write(dasfile['contents'])

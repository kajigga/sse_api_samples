#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import pathlib
import base64
from sseapilib import api
from pprint import pprint

# directory where the files will be exported, Must end with /
import_path = '/tmp/sseexport/'

# it is assumed that any folder inside import_path represents an environment to
# put files into. Normally you would have a single 'base' folder. For example:
# └── base
#     ├── _beacons
#     │   └── status.py
#     ├── apm
#     │   └── install_win.sls
#     ├── custom_repo
#     │   ├── build_rpm.sls
#     │   ├── build_server.sls
#     │   └── files
#     │       └── helloworld.spec
#     ├── git
#     │   └── local.sls
#     ├── grains
#     │   └── set_application_apache.sls
#     ├── patch_example.sls
#     ├── presence
#     │   └── init.sls
#     ├── raas
#     │   ├── update_raas_key.sls
#     │   └── update_ssl_cert.sls
#     ├── service_now.sls
#     └── win
#         ├── verify_patch-2.sls
#         └── verify_patch.sls


def read_decode(filepath):
    """TODO: Docstring for read_decode.
    :returns: TODO

    """
    with open(filepath, "rb") as _f:
        encoded_contents = _f.read()
    return base64.standard_b64encode(encoded_contents).decode()


for (root, dirs, files) in os.walk(import_path, topdown=True):

    for _file in files:
        local_filename = os.path.join(root, _file)

        env, *remote_path = pathlib.PurePath(local_filename[len(import_path):]).parts

        remote_path = str(pathlib.PurePath('/').joinpath(*remote_path))

        # check for file
        get_file = api('fs.get_file',
                       saltenv=env,
                       get_raw=True,
                       path=remote_path)

        if get_file['error']:
            # contents = str(base64.b64encode(open(local_filename).read().encode()))
            contents = read_decode(local_filename)
            # doesn't exist, save it
            res = api('fs.save_file',
                      get_raw=True,
                      saltenv=env,
                      path=remote_path,
                      content_type="binary/octet-stream",
                      contents=contents)

            pprint(res)

        else:
            contents = read_decode(local_filename)
            # file exists, update it
            res = api('fs.update_file',
                      get_raw=True,
                      file_uuid=get_file['ret']['uuid'],
                      saltenv=env,
                      path=remote_path,
                      contents=contents)
            pprint(res)

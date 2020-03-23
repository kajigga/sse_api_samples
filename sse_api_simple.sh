#!/bin/bash

API_HOST='https://sse.kajigga.com'
API_USERNAME=root
# Define the password in ENV variables
# API_PASSWORD="some-secure-password"
TGT_UUID='7f93b928-388b-11e6-b133-346895ecb8f3'

# Step one: authenticate and save xsrf token
curl -k -c $HOME/eAPICookie.txt -u ${API_USERNAME}:${API_PASSWORD} ${API_HOST}/account/login >/dev/null

# Step two, use xsrf token in the header to make the API call
read -r -d '' CMD_TO_RUN <<- EOM
    {
        "resource": "cmd",
        "method": "route_cmd",
        "kwarg": {
            "fun": "state.sls", 
            "cmd": "local",
            "tgt_uuid": "${TGT_UUID}",
            "arg": {
                "arg": ["sync_everything"]
            }
        }
    }
EOM

curl -k -u ${API_USERNAME}:${API_PASSWORD} -b $HOME/eAPICookie.txt \
    -H 'X-Xsrftoken: '$(grep -w '_xsrf' $HOME/eAPICookie.txt | cut -f7)'' \
    -X POST ${API_HOST}/rpc \
    -d "${CMD_TO_RUN}"

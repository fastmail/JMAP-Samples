#!/usr/bin/env python

import json
import os
import sys
import requests

api_uri = "https://betajmap.fastmail.com/api"
auth_uri = "https://betajmap.fastmail.com/authenticate"
username = os.environ.get("JMAP_USERNAME")
password = os.environ.get("JMAP_PASSWORD")

if not username:
    print("no JMAP_USERNAME set!")
    sys.exit(1)

if not password:
    print("no JMAP_PASSWORD set!")
    sys.exit(1)


def get_account_id():
    r = requests.get(auth_uri, auth=(username, password))
    session = r.json()

    account_id = None
    for key, data in session["accounts"].items():
        if data["name"] == username:
            account_id = key
            break

    return account_id


account_id = get_account_id()

get_res = requests.post(
    api_uri,
    auth=(username, password),
    headers={"Content-Type": "application/json"},
    data=json.dumps(
        {
            "using": ["urn:ietf:params:jmap:core", "urn:ietf:params:jmap:mail"],
            "methodCalls": [
                [
                    "Email/query",
                    {
                        "accountId": account_id,
                        "sort": [{"property": "receivedAt", "isAscending": False}],
                        "limit": 10,
                    },
                    "a",
                ],
                [
                    "Email/get",
                    {
                        "accountId": account_id,
                        "properties": ["id", "subject", "receivedAt"],
                        "#ids": {
                            "resultOf": "a",
                            "name": "Email/query",
                            "path": "/ids/*",
                        },
                    },
                    "b",
                ],
            ],
        }
    ),
)
get_res.raise_for_status()

for email in get_res.json()["methodResponses"][1][1]["list"]:
    print("{} - {}".format(email["receivedAt"], email["subject"]))

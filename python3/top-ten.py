#!/usr/bin/env python

import json
import os
from tiny_jmap_library import TinyJMAPClient

client = TinyJMAPClient(
    hostname=os.environ.get("JMAP_HOSTNAME", "betajmap.fastmail.com"),
    username=os.environ.get("JMAP_USERNAME"),
    password=os.environ.get("JMAP_PASSWORD"),
)
account_id = client.get_account_id()

inbox_res = client.make_jmap_call(
    {
        "using": ["urn:ietf:params:jmap:core", "urn:ietf:params:jmap:mail"],
        "methodCalls": [
            [
                "Mailbox/query",
                {
                    "accountId": account_id,
                    "filter": {"role": "inbox", "hasAnyRole": True},
                },
                "a",
            ]
        ],
    }
)
inbox_id = inbox_res["methodResponses"][0][1]["ids"][0]
assert len(inbox_id) > 0

get_res = client.make_jmap_call(
    {
        "using": ["urn:ietf:params:jmap:core", "urn:ietf:params:jmap:mail"],
        "methodCalls": [
            [
                "Email/query",
                {
                    "accountId": account_id,
                    "filter": {"inMailbox": inbox_id},
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
                    "#ids": {"resultOf": "a", "name": "Email/query", "path": "/ids/*"},
                },
                "b",
            ],
        ],
    }
)

for email in get_res["methodResponses"][1][1]["list"]:
    print("{} - {}".format(email["receivedAt"], email["subject"]))

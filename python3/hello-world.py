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

mbox_query = requests.post(
    api_uri,
    auth=(username, password),
    headers={"Content-Type": "application/json"},
    data=json.dumps(
        {
            "using": ["urn:ietf:params:jmap:core", "urn:ietf:params:jmap:mail"],
            "methodCalls": [
                [
                    "Mailbox/query",
                    {"accountId": account_id, "filter": {"name": "Drafts"}},
                    "a",
                ]
            ],
        }
    ),
)

mbox_query.raise_for_status()

draft_mailbox_id = mbox_query.json()["methodResponses"][0][1]["ids"][0]

body = """
Hi!

This email may not look like much, but I sent it with JMAP, a new protocol
designed to make it easier to manage email, contacts, calendars, and more of
your digital life in general.

Pretty cool, right?

-- 
This email sent from my next-generation email system at Fastmail.
"""

draft = {
    "from": [{"email": username}],
    "to": [{"email": username}],
    "subject": "Hello, world!",
    "keywords": {"$draft": True},
    "mailboxIds": {draft_mailbox_id: True},
    "bodyValues": {"body": {"value": body, "charset": "utf-8"}},
    "textBody": [{"partId": "body", "type": "text/plain"}],
}

draft_res = requests.post(
    api_uri,
    auth=(username, password),
    headers={"Content-Type": "application/json"},
    data=json.dumps(
        {
            "using": [
                "urn:ietf:params:jmap:core",
                "urn:ietf:params:jmap:mail",
                "urn:ietf:params:jmap:submission",
            ],
            "methodCalls": [
                [
                    "Email/set",
                    {"accountId": account_id, "create": {"draft": draft}},
                    "a",
                ],
                [
                    "EmailSubmission/set",
                    {
                        "accountId": account_id,
                        "onSuccessDestroyEmail": ["#sendIt"],
                        "create": {"sendIt": {"emailId": "#draft"}},
                    },
                    "b",
                ],
            ],
        }
    ),
)

print(draft_res.text)

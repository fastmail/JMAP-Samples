#!/usr/bin/env python

import json
import os
from tiny_jmap_library import TinyJMAPClient

client = TinyJMAPClient(
    username=os.environ.get("JMAP_USERNAME"), password=os.environ.get("JMAP_PASSWORD")
)
account_id = client.get_account_id()

query_res = client.make_jmap_call(
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
)

draft_mailbox_id = query_res["methodResponses"][0][1]["ids"][0]
assert len(draft_mailbox_id) > 0

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
    "from": [{"email": client.username}],
    "to": [{"email": client.username}],
    "subject": "Hello, world!",
    "keywords": {"$draft": True},
    "mailboxIds": {draft_mailbox_id: True},
    "bodyValues": {"body": {"value": body, "charset": "utf-8"}},
    "textBody": [{"partId": "body", "type": "text/plain"}],
}

create_res = client.make_jmap_call(
    {
        "using": [
            "urn:ietf:params:jmap:core",
            "urn:ietf:params:jmap:mail",
            "urn:ietf:params:jmap:submission",
        ],
        "methodCalls": [
            ["Email/set", {"accountId": account_id, "create": {"draft": draft}}, "a"],
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
)

print(json.dumps(create_res))

import json
import os
import requests


class TinyJMAPClient:
    api_uri = "https://betajmap.fastmail.com/api"
    auth_uri = "https://betajmap.fastmail.com/authenticate"

    def __init__(self, username, password):
        assert len(username) > 0
        assert len(password) > 0

        self.username = username
        self.password = password
        self.account_id = None

    def get_session_resource(self):
        r = requests.get(self.auth_uri, auth=(self.username, self.password))
        return r.json()

    def get_account_id(self):
        if self.account_id:
            return self.account_id

        session = self.get_session_resource()

        account_id = None
        for key, data in session["accounts"].items():
            if data["name"] == self.username:
                account_id = key
                break

        self.account_id = account_id
        return self.account_id

    def make_jmap_call(self, call):
        res = requests.post(
            self.api_uri,
            auth=(self.username, self.password),
            headers={"Content-Type": "application/json"},
            data=json.dumps(call),
        )
        res.raise_for_status()
        return res.json()

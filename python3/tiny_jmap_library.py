import json
import os
import requests


class TinyJMAPClient:
    """The tiniest JMAP client you can imagine."""

    api_uri = "https://betajmap.fastmail.com/api"
    auth_uri = "https://betajmap.fastmail.com/authenticate"

    def __init__(self, username, password):
        """Initialize using a username and password"""
        assert len(username) > 0
        assert len(password) > 0

        self.username = username
        self.password = password
        self.account_id = None

    def get_session_resource(self):
        """Return the JMAP Session Resource as a Python dict"""
        r = requests.get(self.auth_uri, auth=(self.username, self.password))
        r.raise_for_status()
        return r.json()

    def get_account_id(self):
        """Return the accountId for the account matching self.username"""
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
        """Make a JMAP POST request to the API, returning the reponse as a
        Python data structure."""
        res = requests.post(
            self.api_uri,
            auth=(self.username, self.password),
            headers={"Content-Type": "application/json"},
            data=json.dumps(call),
        )
        res.raise_for_status()
        return res.json()

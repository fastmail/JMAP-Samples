import json
import os
import requests


class TinyJMAPClient:
    """The tiniest JMAP client you can imagine."""

    def __init__(self, hostname, username, password):
        """Initialize using a hostname, username and password"""
        assert len(hostname) > 0
        assert len(username) > 0
        assert len(password) > 0

        self.hostname = hostname
        self.username = username
        self.password = password
        self.session = None
        self.api_url = None
        self.account_id = None

    def get_session(self):
        """Return the JMAP Session Resource as a Python dict"""
        if self.session:
            return self.session
        r = requests.get(
            "https://" + self.hostname + "/.well-known/jmap",
            auth=(self.username, self.password),
        )
        r.raise_for_status()
        self.session = session = r.json()
        self.api_url = session["apiUrl"]
        return session

    def get_account_id(self):
        """Return the accountId for the account matching self.username"""
        if self.account_id:
            return self.account_id

        session = self.get_session()

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
            self.api_url,
            auth=(self.username, self.password),
            headers={"Content-Type": "application/json"},
            data=json.dumps(call),
        )
        res.raise_for_status()
        return res.json()

import json
import requests


class TinyJMAPClient:
    """The tiniest JMAP client you can imagine."""

    def __init__(self, hostname, username, token):
        """Initialize using a hostname, username and bearer token"""
        assert len(hostname) > 0
        assert len(username) > 0
        assert len(token) > 0

        self.hostname = hostname
        self.username = username
        self.token = token
        self.session = None
        self.api_url = None
        self.account_id = None
        self.identity_id = None

    def get_session(self):
        """Return the JMAP Session Resource as a Python dict"""
        if self.session:
            return self.session
        r = requests.get(
            "https://" + self.hostname + "/.well-known/jmap",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.token}",
            },
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

        account_id = session["primaryAccounts"]["urn:ietf:params:jmap:mail"]
        self.account_id = account_id
        return account_id

    def get_identity_id(self):
        """Return the identityId for an address matching self.username"""
        if self.identity_id:
            return self.identity_id

        identity_res = self.make_jmap_call(
            {
                "using": [
                    "urn:ietf:params:jmap:core",
                    "urn:ietf:params:jmap:submission",
                ],
                "methodCalls": [
                    ["Identity/get", {"accountId": self.get_account_id()}, "i"]
                ],
            }
        )

        identity_id = next(
            filter(
                lambda i: i["email"] == self.username,
                identity_res["methodResponses"][0][1]["list"],
            )
        )["id"]

        self.identity_id = str(identity_id)
        return self.identity_id

    def make_jmap_call(self, call):
        """Make a JMAP POST request to the API, returning the reponse as a
        Python data structure."""
        res = requests.post(
            self.api_url,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.token}",
            },
            data=json.dumps(call),
        )
        res.raise_for_status()
        return res.json()

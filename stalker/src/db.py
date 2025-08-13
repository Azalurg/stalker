import logging

import couchdb
import requests

logger = logging.getLogger(__name__)


class Store:
    def __init__(
        self, username, password, dbname, host="127.0.0.1", port="5984", protocol="http"
    ):
        self._username = username
        self._password = password
        self._host = host
        self._port = port
        self._protocol = protocol
        self._dbname = dbname

        self._url = "{}://{}:{}@{}:{}".format(
            self._protocol, self._username, self._password, self._host, self._port
        )
        self._server = couchdb.Server(self._url)

        try:
            self.db = self._server.create(self._dbname)
        except couchdb.http.PreconditionFailed:
            self.db = self._server[self._dbname]

        self._ensure_wallet_indexes()

    def _ensure_wallet_indexes(self):
        url = f"{self._url}/{self._dbname}/_index"
        payload = {
            "index": {"fields": ["name", "created_at"]},
            "name": "wallet_indexes",
            "type": "json",
        }
        response = requests.post(
            url, json=payload, headers={"Content-Type": "application/json"}
        )
        if response.status_code not in [200, 201]:
            logger.error("Creating indexes failed", response.text)

    # def add_doc(self, doc):
    #     return self.db.save(doc)

    def get_doc_by_id(self, doc_id):
        return self.db[doc_id]

    def find_wallet_by_name(self, name):
        selector = {"name": name}
        results = self.db.find(
            {"selector": selector, "limit": 1, "sort": [{"created_at": "desc"}]}
        )
        docs = list(results)
        return docs[0] if docs else None

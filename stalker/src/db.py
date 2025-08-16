import logging
import os

import couchdb
import requests

logger = logging.getLogger(__name__)


class Store:
    def __init__(self):
        self._username = os.getenv("COUCHDB_USERNAME", "admin")
        self._password = os.getenv("COUCHDB_PASSWORD", "password")
        self._host = os.getenv("COUCHDB_HOST", "localhost")
        self._port = os.getenv("COUCHDB_PORT", "5984")
        self._protocol = os.getenv("COUCHDB_PROTOCOL", "http")
        self._dbname = os.getenv("COUCHDB_DBNAME", "stalker")

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

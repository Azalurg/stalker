import couchdb


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
            self._db = self._server.create(self._dbname)
        except couchdb.http.PreconditionFailed:
            self._db = self._server[self._dbname]

    def add_doc(self, doc):
        return self._db.save(doc)

    def get_doc_by_id(self, doc_id):
        return self._db[doc_id]

from datetime import datetime
from couchdb.mapping import (
    Document,
    TextField,
    IntegerField,
    FloatField,
    ListField,
    DictField,
)


class Asset(Document):
    name = TextField()
    units = FloatField()
    average_purchase_price = FloatField()
    current_price = FloatField()
    value = FloatField()
    assets_share = FloatField()
    change = FloatField()
    profit = FloatField()
    investment_period = IntegerField()
    timestamp = TextField(default=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


class Snapshot(Document):
    assets = ListField(DictField())
    timestamp = TextField(default=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


class Wallet(Document):
    name = TextField()
    url = TextField()
    snapshot = DictField()
    created_at = TextField(default=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    last_updated = TextField(
        default=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )

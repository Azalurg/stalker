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

    def as_dict(self):
        """Convert Asset object to dictionary for JSON serialization"""
        return {
            "name": self.name,
            "units": self.units,
            "average_purchase_price": self.average_purchase_price,
            "current_price": self.current_price,
            "value": self.value,
            "assets_share": self.assets_share,
            "change": self.change,
            "profit": self.profit,
            "investment_period": self.investment_period,
            "timestamp": self.timestamp,
        }


class Snapshot(Document):
    assets = ListField(DictField())
    timestamp = TextField(default=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    def as_dict(self):
        """Convert Snapshot object to dictionary for JSON serialization"""
        assets_data = []
        for asset in self.assets:
            assets_data.append(asset.as_dict())

        return {"assets": assets_data, "timestamp": self.timestamp}


class Wallet(Document):
    name = TextField()
    url = TextField()
    snapshots = ListField(DictField())
    created_at = TextField(default=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    last_updated = TextField(
        default=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )

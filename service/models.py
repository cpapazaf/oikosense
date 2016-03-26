from peewee import SqliteDatabase, Model, CharField
import logging
import json
import datetime

logger = logging.getLogger("arduino.server")
db = SqliteDatabase(None)


class BaseModel(Model):
    class Meta:
        database = db

    def to_json(self):
        r = {}
        for k in self._data.keys():
            r[k] = getattr(self, k)
            if isinstance(r[k], datetime.date):
                r[k] = [r[k].year, r[k].month, r[k].day]
            elif isinstance(r[k], datetime.time):
                r[k] = [r[k].hour, r[k].minute, r[k].second]
            elif isinstance(r[k], Model):
                r[k] = r[k].to_json()
        return r

    def __str__(self):
        print(self.to_json())
        return json.dumps(self.to_json())


class Settings(BaseModel):
    key = CharField()
    value = CharField()


def init(path=':memory:'):
    db.init(path)
    db.connect()
    logger.info("Creating DB tables...")
    Settings.create_table(True)

import logging
import tornado
import http

from .handlers import BaseHandler

from service.models import Settings

logger = logging.getLogger("arduino.server")


class SettingsHandler(BaseHandler):
    SUPPORTED_METHODS = ('GET', 'POST', 'PUT', 'DELETE')

    def get(self):
        settings_list = list()
        for set in Settings.select():
            settings_list.append(set.to_json())
        self.write(tornado.escape.json_encode(settings_list))

    def post(self):
        resp = Settings.create(key=self.payload['key'], value=self.payload['value'])
        self.set_status(200)
        self.write(str(resp))

    def put(self):
        Settings.update(value=self.payload['value']).where(Settings.key == self.payload['key']).execute()
        self.set_status(200)
        self.write("ok")

    def delete(self):
        resp = Settings.get(Settings.key == self.payload['key'])
        if resp:
            resp.delete_instance()
            self.set_status(200)
            self.write(str(resp))
        else:
            self.set_status(404)
            self.write(self.payload['key'] + "not in database")

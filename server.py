#!/usr/bin/env python
import base64
import logging
import os
import uuid
import tornado.httpserver
from tornado.options import define, options
import tornado.web
from service.models import init
from soners.soners_server import SonersServer
from service.handlers.handlers_settings import SettingsHandler
from service.handlers.handlers import InfoHandler, CurentStatusHandler, TemplateHandler, ErrorHandler, StreamHandler
from service.handlers.sensor_handlers import temperature_handler, humidity_handler, motion_handler

logger = logging.getLogger("arduino.server")
www_static_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'www', 'static'))
www_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'www'))

define('config', default='server.conf', help='full path to the configuration file')
define('debug', default=False, help='debug True False')
define('port', default='8080', help='port to start server on', group='application')
define('database_file', default=':memory:', help='full path to database', group='application')
define('arduino_tty', default=None, help='usb serial port for arduino', group='application')
define('storage_location', default='./', help='location in the disk to store logs and images', group='application')
define('mail_from', default=None, help='email to use as From', group='application')
define('mail_to', default=None, help='email to use as To', group='application')
define('mail_login_uname', default=None, help='email to login to smtp with', group='application')
define('mail_login_passwd', default=None, help='passwd to login to smtp with', group='application')

web_urls = [
    (r'/api/info', InfoHandler),
    (r'/api/v1/status', CurentStatusHandler),
    (r'/api/v1/stream/(.*)', StreamHandler),
    (r'/api/v1/settings', SettingsHandler),
    (r'/', TemplateHandler),
    tornado.web.URLSpec(r'/static/(.*)', tornado.web.StaticFileHandler, {'path': www_static_path}, name='static')
]

hermes_urls = [
    ('^T:(?P<temperature>.*)$', temperature_handler),
    ('^H:(?P<humidity>.*)$', humidity_handler),
    ("^M:(?P<motion>.*)$", motion_handler)
]


def setup_application(app_options):
    settings = {
        'template_path': www_path,
        'cookie_secret': base64.b64encode(uuid.uuid4().bytes + uuid.uuid4().bytes),
    }

    settings.update(app_options)

    application = tornado.web.Application(web_urls, **settings)
    tornado.web.ErrorHandler = ErrorHandler

    return application


def main():
    tornado.options.parse_command_line()

    if options.config:
        config_to_read = options.config
    else:
        config_to_read = './server.conf'

    tornado.options.parse_config_file(config_to_read)

    if options.debug:
        logging.getLogger("arduino.server").setLevel(logging.DEBUG)

    init(options.database_file)

    http_server = tornado.httpserver.HTTPServer(setup_application(options.group_dict('application')))
    http_server.listen(os.getenv('OIKOSENSE_PORT', options.port))

    if os.getenv('OIKOSENSE_ARDUINO_TTY', options.arduino_tty):
        hermes_server = SonersServer(hermes_urls)
        hermes_server.listen(os.getenv('OIKOSENSE_ARDUINO_TTY', options.arduino_tty))

    tornado.ioloop.IOLoop.instance().start()


if __name__ == '__main__':
    main()

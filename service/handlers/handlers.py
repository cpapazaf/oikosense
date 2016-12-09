import tornado.httpserver
import tornado.web
from tornado.options import options
import logging
import os
import base64
import uuid
import http
import resource
import traceback
import time
from time import gmtime, strftime
import datetime
import subprocess

logger = logging.getLogger("arduino.server")


class BaseHandler(tornado.web.RequestHandler):
    @property
    def videocapture(self):
        return self.application.settings.get('videocapture')

    @tornado.gen.coroutine
    def log_exception(self, exc_type, exc_value, exc_traceback):
        logger.warning("Exception %s" % exc_value)
        if (not isinstance(exc_value, tornado.web.HTTPError)) or (exc_value.status_code >= http.client.INTERNAL_SERVER_ERROR):
            stacktrace = ''.join(traceback.format_tb(exc_traceback))
            logger.error("Stacktrace %s" % stacktrace)

    @tornado.gen.coroutine
    def write_error(self, status_code, **kwargs):
        if status_code == 404:
            message = None
            if 'exc_info' in kwargs and\
                    kwargs['exc_info'][0] == tornado.web.HTTPError:
                    message = kwargs['exc_info'][1].log_message
            self.write(message)
        elif status_code == 500:
            error_trace = ""
            for line in traceback.format_exception(*kwargs['exc_info']):
                error_trace += line

            self.write('Server Error: ' + str(error_trace))
        else:
            message = None
            if 'exc_info' in kwargs and\
                    kwargs['exc_info'][0] == tornado.web.HTTPError:
                    message = kwargs['exc_info'][1].log_message
                    self.set_header('Content-Type', 'text/plain')
                    self.write(str(message))
            self.set_status(status_code)

    def set_default_headers(self):
        pass
#        self.set_header("Access-Control-Allow-Origin", "*")

    def prepare(self):
        self.payload = {}
        if len(self.request.body) == 0:
            return
        try:
            self.payload = tornado.escape.json_decode(self.request.body)
            if isinstance(self.payload, list):  # this is from JS
                self.payload = dict([[e['name'], e['value']] for e in self.payload])
        except ValueError:
            logger.error('could not decode %r' % self.request.body)


class InfoHandler(BaseHandler):
    SUPPORTED_METHODS = ('GET',)

    def get(self):
        """Read server parameter

           :status 200: ok
        """
        data = options.as_dict()
        data.update({'rootpath': os.path.dirname(__file__),
                     'memory': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss})
        self.write(data)


class CurentStatusHandler(BaseHandler):
    SUPPORTED_METHODS = ('GET',)

    def get(self):
        """Read server parameter

           :status 200: ok
        """
        humidity_content = []
        temperature_content = []

        try:
            with open(os.path.join(self.application.settings["storage_location"], "humidity.log"), "r") as myfile:
                myfile.seek (0, 2)           # Seek @ EOF
                fsize = myfile.tell()        # Get Size
                myfile.seek (max (fsize-1024, 0), 0) # Set pos @ last n chars
                humidity_lines = myfile.readlines()       # Read to end

            humidity_content = humidity_lines[-60:]    # Get last 60 lines
        except EnvironmentError:
            logger.error('Couldnt open humidity.log')
            
        try:
            with open(os.path.join(self.application.settings["storage_location"], "temperature.log"), "r") as myfile:
                myfile.seek (0, 2)           # Seek @ EOF
                fsize = myfile.tell()        # Get Size
                myfile.seek (max (fsize-1024, 0), 0) # Set pos @ last n chars
                temperature_lines = myfile.readlines()       # Read to end

            temperature_content = temperature_lines[-60:]    # Get last 60 lines
        except EnvironmentError:
            logger.error('Couldnt open temperature.log')

        humidity_list = []

        for pos, ard_line in enumerate(humidity_content):
            import re
            ard_re = re.compile(r'(?P<date>.*)\t(?P<hum>.*)')
            m = ard_re.match(humidity_content[pos].rstrip())
            if m:
                try:
                    humidity_list.append({
                        'date': m.group('date').rstrip(),
                        'humidity': float(m.group('hum').rstrip())
                    })
                except:
                    pass

        temperature_list = []

        for pos, ard_line in enumerate(temperature_content):
            import re
            ard_re = re.compile(r'(?P<date>.*)\t(?P<temp>.*)')
            m = ard_re.match(temperature_content[pos].rstrip())
            if m:
                try:
                    temperature_list.append({
                        'date': m.group('date').rstrip(),
                        'temperature': float(m.group('temp').rstrip())
                    })
                except:
                    pass

        result = {'temperature': temperature_list, 'humidity': humidity_list}

        self.write(tornado.escape.json_encode(result))

    
class ErrorHandler(BaseHandler):
    """Generates an error response with status_code for all requests."""
    def initialize(self, status_code):
        self._status_code = status_code

    def write_error(self, status_code, **kwargs):
        if status_code == http.client.NOT_FOUND:
            self.write('Oups! Are you lost ?')
        elif status_code == http.client.METHOD_NOT_ALLOWED:
            self.write('Oups! Method not allowed.')

    def prepare(self):
        raise tornado.web.HTTPError(self._status_code)


class TemplateHandler(BaseHandler):
    def get(self, template_name="index"):
        tpl_vars = {}
        tpl_path = os.path.isfile(os.path.join(self.application.settings['template_path'], "%s.html" % template_name))
        if not tpl_path:
            raise tornado.web.HTTPError(http.client.NOT_FOUND, 'template %r not found' % template_name)
        tpl_vars.update(dict([[name, self.get_argument(name)] for name in self.request.arguments.keys()]))
        tpl_vars.update(dict([['server_protocol', self.request.protocol], ['server_host', self.request.host]]))
        try:
            self.render("%s.html" % template_name, **tpl_vars)
        except Exception as ex:
            tpl_vars = {'template': template_name, 'error': ex.args}
            self.render("template_error.html", **tpl_vars)


class StreamHandler(tornado.web.RequestHandler):
    SUPPORTED_METHODS = ('GET')

    @tornado.gen.coroutine
    def get(self, action):

        def stop_omxplayer():
            logger.info('will stop all playing songs')
            process = subprocess.Popen('killall omxplayer', shell=True)
            process = subprocess.Popen("ps -ef | grep omxplayer | grep -v grep | awk '{print $2}'| xargs kill", shell=True)


        if action == 'play':
            stop_omxplayer()
            logger.info('play omxplayer {}'.format(self.get_argument("stream", None, None)))
            if self.get_argument("stream", None, None): 
                process = subprocess.Popen('/usr/bin/omxplayer ' + self.get_argument("stream", None, None), shell=True)
                self.write('Playing stream {}'.format(self.get_argument("stream", None, None)))
            else:
                self.finish('please provice steam arguments like ?stream=http://realfm.megabyte.gr:8999/')
        if action == 'stop':
            stop_omxplayer()            
            self.write("Stopped omxplayer")



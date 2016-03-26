from fabric.api import *
import os
import inspect
from fabric.contrib.files import exists
from time import gmtime, strftime

env.hosts = ['192.168.0.13']
env.user = 'pi'
env.password = 'raspberry'

curent_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

def deploy():
    run('sudo supervisorctl stop iot-server')
    run('mkdir -p /home/pi/iot-server')
    run('rm -rf /home/pi/iot-server/*')
    put(curent_dir + os.sep + '*', '/home/pi/iot-server')
    with cd('/home/pi/iot-server/'):
        run('sudo pip3 install -r requirements.txt')
    try:
        run('sudo supervisorctl start iot-server')
    except:
        run('sudo tail -F /var/log/supervisor/iot-server-stderr-*.log')



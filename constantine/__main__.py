import configparser
import datetime
import getpass
import sys
import time
import traceback

from constantine.api import Constantine

config = configparser.ConfigParser()
config.read('config.conf')

token = config['main']['bot_token']
jenkins_url = config['main']['jenkins_url']
jobs_names = dict(config['jobs'])

jenkins_username = input('jenkins username:')
jenkins_password = getpass.getpass(prompt='jenkins password:')

while True:
    monsieur = Constantine(token, jenkins_url, jenkins_username,
                           jenkins_password, jobs_names)
    try:
        monsieur.wake_up()
    except Exception as ex:
        monsieur.bot.stop_polling()
        monsieur.bot.worker_pool.close()
        sys.stdout.write('\n\n\n' + '=' * 42 + '\n')
        sys.stdout.write('{}\n'.format(datetime.datetime.now()))
        traceback.print_exception(*sys.exc_info())
        sys.stdout.write('\n' + str(ex))
        sys.stdout.write('\nRestart loop!\n' + '=' * 42 + '\n')
        time.sleep(5)
    else:
        break

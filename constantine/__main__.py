import configparser
import getpass

from constantine.api import Constantine

config = configparser.ConfigParser()
config.read('../config.conf')

token = config['main']['bot_token']
jenkins_url = config['main']['jenkins_url']
jobs_names = dict(config['jobs'])

jenkins_username = input('jenkins username:')
jenkins_password = getpass.getpass(prompt='jenkins password:')

monsieur = Constantine(token, jenkins_url, jenkins_username, jenkins_password,
                       jobs_names)
monsieur.wake_up()

import paramiko
from django.conf import settings
from src.config import config

class ssh:
    conf = config(settings.DBA_CONFIG_FILE)
    connection = None
    host = None

    def __init__(self, host):
        self.host = host
        self.conf = config(settings.DBA_CONFIG_FILE)['dba']['ssh'][self.host]

    def open(self):
        self.connection = paramiko.SSHClient()
        self.connection.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.connection.connect(self.conf['host'], username=self.conf['user'], password=self.conf['pass'])

    def cmd(self, command, env=None):
        stdin, stdout, stderr = self.connection.exec_command(command, get_pty=True, environment=env)
        stdin.channel.shutdown_write()
        messages = [x for x in stdout]
        error = [x for x in stderr]
        return messages, error
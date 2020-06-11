from src.db import mssql, mysql, oracle
from . import general


class DbListApp():
    conf = None
    instance_name = None
    host_name = None
    driver = None
    db = None

    def __init__(self, config):
        self.conf = config

    def get_instance_list(self, host, selected=None):
        for item in self.conf['dba']['database']['hosts']:
            if item['name'] == host and 'instances' in item:
                instances = []
                for instance in item['instances']:
                    if selected is not None and selected == instance['name']:
                        instance.update({'selected': 'selected="selected"'})
                        self.instance_name = instance['name']
                    else:
                        instance.update({'selected': ''})
                    instances.append(instance)
                return instances
        return []

    def get_hosts(self, selected=None):
        hosts = self.conf['dba']['database']['hosts']
        content = []
        for host in hosts:
            if selected is not None and selected == host['name']:
                host.update({'selected': 'selected="selected"'})
                self.host_name = host['name']
            else:
                host.update({'selected': ''})
            content.append(host)
        return content

    def get_db_config(self):
        return general.prepare_config(self.conf, self.host_name, self.instance_name)

    def get_db_connection(self):
        config = self.get_db_config()
        self.driver = config['driver']
        if self.driver == 'MSSQL':
            self.db = mssql
        elif self.driver == 'MySQL':
            self.db = mysql
        elif self.driver == 'Oracle':
            self.db = oracle
        return self.db.create(config)

    def get_db_list(self):
        connection = self.get_db_connection()
        itemlist = self.db.query(connection, 'db_list_size')
        return itemlist

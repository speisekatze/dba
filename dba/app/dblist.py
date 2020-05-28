from src.db import mssql, mysql, oracle
from . import general


class DbListApp():
    conf = None
    instance_name = None
    host_name = None

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

    def get_db_list(self):
        config = general.prepare_config(self.conf, self.host_name, self.instance_name)
        if config['driver'] == 'MSSQL':
            db = mssql
        elif config['driver'] == 'MySQL':
            db = mysql
        elif config['driver'] == 'Oracle':
            db = oracle
        else:
            db = None
        connection = db.create(config)
        itemlist = db.query(connection, 'db_list_size', {})
        return itemlist

# maybe later - get_object_or_404
from django.shortcuts import render
from datetime import date
# maybe later - reverse
from django.views import generic
from src.config import config
from src.db import mssql, mysql, oracle, sqlite
from .forms import SucheForm
import re


# Create your views here.
def get_default_data():
    data = {}
    data['headline'] = 'Datenbank Admin'
    return data


class IndexView(generic.FormView):
    template_name = 'dba/index.html'
    conf = config('config/config.yml')
    form_class = SucheForm
    instance_name = None
    host_name = None

    def get(self, request, *args, **kwargs):
        host_list = self.get_hosts()
        context = get_default_data()
        context['seite'] = 'Übersicht'
        context['host_list'] = host_list
        context['form'] = SucheForm(host_list)
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        host = request.POST.get('hosts')
        instance = request.POST.get('instances')
        host_list = self.get_hosts(host)
        context = get_default_data()
        context['form'] = SucheForm(host_list)
        context['host_list'] = host_list
        context['seite'] = 'Übersicht'
        context['instance_list'] = self.get_instance_list(host, instance)
        if (request.POST.get('suchen') == 'Suchen'):
            dev = umgebungen_laden(self.conf, host, instance)
            beta = umgebungen_laden(self.conf, host, instance)
            release = umgebungen_laden(self.conf, host, instance)
            dbt = connect_dbt(self.conf)
            vernichten = load_dbt(dbt)
            db_tuples = self.get_db_list(self.host_name, self.instance_name)
            context['db_list'] = []
            for db in db_tuples:
                items = {}
                info = find_in_dbt(vernichten, self.instance_name, db[0])
                items['umgebung'] = 'DEV: ' + umgebung_suchen(dev, db[0])
                items['umgebung'] += "\r\n" + 'BETA: ' + umgebung_suchen(beta, db[0])
                items['umgebung'] += "\r\n" + 'RELEASE: ' + umgebung_suchen(release, db[0])
                items['name'] = db[0]
                items['size'] = db[1]
                items['log'] = db[2]
                items['sum'] = db[3]
                items['add'] = db[4]
                if info:
                    items['delete'] = date.fromtimestamp(info)
                    items['delta'] = (items['delete'] - date.today()).days
                else:
                    items['delete'] = 'nicht gefunden'
                    items['delta'] = -9000
                context['db_list'].append(items)
        return render(request, self.template_name, context)

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

    def get_db_list(self, host, instance=None):
        conf = prepare_config(self.conf, host, instance)
        if conf['driver'] == 'MSSQL':
            db = mssql
        elif conf['driver'] == 'MySQL':
            db = mysql
        elif conf['driver'] == 'Oracle':
            db = oracle
        else:
            db = None
        connection = db.create(conf)
        itemlist = db.query(connection, 'db_list_size', {})
        return itemlist


def prepare_config(configuration, host, instance=None):
    conf = {}
    for item in configuration['dba']['database']['hosts']:
        if item['name'] == host:
            conf['server'] = item['fqdn']
            conf['driver'] = item['driver']
            if 'lde_conf' in item:
                conf['lde_conf'] = item['lde_conf']
            conf['database'] = ''
            if instance is not None:
                conf['instance'] = prepare_instance_config(item, instance)
            conf['user'] = item['user']
            conf['password'] = item['password']
            if 'instance' in conf:
                if 'user' in conf['instance'] and 'password' in conf['instance']:
                    conf['user'] = conf['instance']['user']
                    conf['password'] = conf['instance']['password']
                conf['instance'] = conf['instance']['name']
    return conf


def prepare_instance_config(item, instance):
    conf = None
    if 'instances' in item:
        for inst in item['instances']:
            if instance == inst['name']:
                conf = inst
    else:
        # Error
        print('Fehler')
    return conf


def connect_dbt(conf):
    print()
    dbt_conf = {
        'user': conf['dba']['dbt']['user'],
        'password': conf['dba']['dbt']['password'],
        'server': conf['dba']['dbt']['fqdn'],
        'database': conf['dba']['dbt']['database']
    }
    return mysql.create(dbt_conf)


def load_dbt(connection):
    dbt = mysql.query(connection, 'db_dbt_all')
    return dbt


def find_in_dbt(dbt, instance, db_name):
    result = None
    pattern = None
    if instance is None:
        pattern = re.compile(r'\w - ' + db_name + '$')
    else:
        pattern = re.compile(instance + ' - ' + db_name + '$')
    for db in dbt:
        if pattern.search(db[1]):
            result = db[0]
    return result


def umgebungen_laden(conf, host, instance):
    dev_db = sqlite.create(conf['dba']['lde']['dev'])
    db_conf = prepare_config(conf, host, instance)
    if db_conf['driver'] == 'MSSQL':
        dev = sqlite.query(dev_db, 'umgebungen', [host + '\\' + instance])
    else:
        dev = sqlite.query(dev_db, 'umgebungen', [db_conf['lde_conf']])
    return dev


def umgebung_suchen(umgebungen, db_name):
    for umgebung in umgebungen:
        if db_name == umgebung[0].decode("cp1252"):
            return umgebung[1].decode("cp1252")
    return ''

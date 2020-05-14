# maybe later - get_object_or_404
from django.shortcuts import render
# maybe later - reverse
from django.views import generic
from src.config import config
from src.db import mssql
from .forms import SucheForm


# Create your views here.
def get_default_data():
    data = {}
    data['headline'] = 'Datenbank Admin'
    return data


class IndexView(generic.FormView):
    template_name = 'dba/index.html'
    conf = config('config/config.yml')
    form_class = SucheForm

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
        # context['debugmessage'] = request.POST
        context['seite'] = 'Übersicht'
        context['instance_list'] = self.get_instance_list(host, instance)
        if (request.POST.get('suchen') == 'Suchen'):
            context['db_list'] = self.get_db_list(host, instance)
        return render(request, self.template_name, context)

    def get_instance_list(self, host, selected=None):
        for item in self.conf['dba']['database']['hosts']:
            if item['name'] == host and 'instances' in item:
                instances = []
                for instance in item['instances']:
                    if selected is not None and selected == instance['name']:
                        instance.update({'selected': 'selected="selected"'})
                    instances.append(instance)
                return instances
        return []

    def get_hosts(self, selected=None):
        hosts = self.conf['dba']['database']['hosts']
        content = []
        for host in hosts:
            if selected is not None and selected == host['name']:
                host.update({'selected': 'selected="selected"'})
            else:
                host.update({'selected': ''})
            content.append(host)
        return content

    def get_db_list(self, host, instance=None):
        conf = prepare_config(self.conf, host, instance)
        if conf['driver'] == 'MSSQL':
            db = mssql
        else:
            db = None
        connection = db.create(conf)
        itemlist = db.query(connection, 'db_list_size')
        return itemlist


def prepare_config(configuration, host, instance=None):
    conf = {}
    for item in configuration['dba']['database']['hosts']:
        if item['name'] == host:
            conf['server'] = item['fqdn']
            conf['driver'] = item['driver']
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

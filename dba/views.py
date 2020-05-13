# from django.shortcuts import get_object_or_404, render
# from django.urls import reverse
from django.views import generic
from src.config import config
from src.db import mssql


# Create your views here.
def get_default_data():
    data = {}
    data['headline'] = 'Datenbank Admin'
    return data


class IndexView(generic.TemplateView):
    template_name = 'dba/index.html'
    context_object_name = 'host_list'
    conf = config('config/config.yml')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_default_data())
        context['seite'] = 'Übersicht'
        context['host_list'] = self.get_hosts()
        print(context['host_list'])
        return context

    def get_database_list(self):    
        hosts = self.conf['dba']['database']['hosts']
        dbs = {}
        return hosts

    def get_hosts(self):
        hosts = self.conf['dba']['database']['hosts']
        content = []
        for host in hosts:
            content.append(host)
        return content
            
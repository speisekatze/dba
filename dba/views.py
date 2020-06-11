# maybe later - get_object_or_404
from django.conf import settings
from django.shortcuts import render
from datetime import date
# maybe later - reverse
from django.views import generic
from src.config import config
from .app import general
from .app.dblist import DbListApp
from .forms import NewDbForm


# Create your views here.
def get_default_data():
    data = {}
    data['headline'] = 'Datenbank Admin'
    return data


class IndexView(generic.FormView):
    template_name = 'dba/index.html'
    conf = config(settings.DBA_CONFIG_FILE)
    seite = 'Nicht Benutzt'

    def get(self, request, *args, **kwargs):
        context = get_default_data()
        context['seite'] = self.seite

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = get_default_data()
        context['seite'] = self.seite

        return render(request, self.template_name, context)


class NewDBView(generic.FormView):
    template_name = 'dba/newdb.html'
    conf = config(settings.DBA_CONFIG_FILE)
    form_class = NewDbForm

    def get(self, request, *args, **kwargs):
        context = get_default_data()
        context['seite'] = 'Neue Datenbank'
        context['host_name'] = kwargs['host']
        context['instance_name'] = kwargs['instance']
        context['form'] = self.form_class
        return render(request, self.template_name, context)


class DbListView(generic.FormView):
    template_name = 'dba/index.html'
    conf = config(settings.DBA_CONFIG_FILE)
    seite = 'Übersicht'

    def get(self, request, *args, **kwargs):
        dblist = DbListApp(self.conf)
        host_list = dblist.get_hosts()
        context = get_default_data()
        context['seite'] = self.seite
        context['host_list'] = host_list
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        dblist = DbListApp(self.conf)
        host = request.POST.get('hosts')
        instance = request.POST.get('instances')
        host_list = dblist.get_hosts(host)
        context = get_default_data()
        context['host_list'] = host_list
        context['host_name'] = dblist.host_name
        context['instance_list'] = dblist.get_instance_list(host, instance)
        context['instance_name'] = dblist.instance_name
        show_list = False
        if (request.POST.get('shrink')):
            connection = dblist.get_db_connection()
            dblist.db.query(connection, 'shrink', [request.POST.get('db_name')])
            show_list = True
        if (request.POST.get('simple')):
            connection = dblist.get_db_connection()

            dblist.db.query_format(connection, 'simple', request.POST.get('db_name'))
            show_list = True
        if (request.POST.get('select') == 'Auswahl'):
            context['debugmessage'] = ''
        if (request.POST.get('suchen') == 'Suchen' or show_list):
            context['seite'] = self.seite
            context['db_list'] = self.suchen(dblist)
            context['db_driver'] = dblist.driver
        return render(request, self.template_name, context)

    def suchen(self, dblist):
        dev = general.umgebungen_laden(self.conf, 'dev', dblist.host_name,
                                       dblist.instance_name)
        beta = general.umgebungen_laden(self.conf, 'beta', dblist.host_name,
                                        dblist.instance_name)
        release = general.umgebungen_laden(self.conf, 'release', dblist.host_name, 
                                           dblist.instance_name)
        dbt = general.connect_dbt(self.conf)
        vernichten = general.load_dbt(dbt)
        db_tuples = dblist.get_db_list()
        db_list = []
        for db in db_tuples:
            items = {}
            info = general.find_in_dbt(vernichten, dblist.instance_name, db[0])
            items['umgebung'] = 'DEV: ' + general.umgebung_suchen(dev, db[0])
            items['umgebung'] += "\r\n" + 'BETA: ' + general.umgebung_suchen(beta, db[0])
            items['umgebung'] += "\r\n" + 'RELEASE: ' + general.umgebung_suchen(release, db[0])
            items['name'] = db[0]
            items['size'] = db[1]
            items['log'] = db[2]
            items['sum'] = db[3]
            items['add'] = db[4]
            if info:
                items['delete'] = date.fromtimestamp(info[0])
                items['dbtid'] = info[2]
                items['delta'] = (items['delete'] - date.today()).days
            else:
                items['delete'] = 'nicht gefunden'
                items['delta'] = -9000
            db_list.append(items)
        return db_list

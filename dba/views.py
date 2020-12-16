# maybe later - get_object_or_404
from django.conf import settings
from django.shortcuts import render, redirect
from datetime import date, datetime#
# maybe later - reverse
from django.views import generic
from src.config import config
from .app import general
from .app.dblist import DbListApp
from .forms import NewDbForm
from src.db import mysql, sqlite


# Create your views here.
def get_default_data():
    data = {}
    data['headline'] = 'Datenbank Admin'
    data['pass_css_class'] = 'navigation'
    data['polls_css_class'] = 'navigation'
    data['dba_css_class'] = 'navigationActive'
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
    success_url = '/dba/newdb/success'

    def form_valid(self, form):
        dbt = general.connect_dbt(self.conf)
        # grund_id, eingespielt_von, eingespielt_am, verschluesselt, passwort, ziel_db, umgebung_dev, umgebung_beta, umgebung_release, createuser, createtime
        data = {}
        data['kunden_id'] = form.cleaned_data['kunden']
        data['grund_id'] = 1
        data['eingespielt_von'] = ''.join(["%0.2x" % int(x) for x in self.request.user.objid])
        data['eingespielt_am'] = int(datetime.now().timestamp())
        if form.cleaned_data['passwort'] != '':
            form.cleaned_data['verschluesselt'] = 'j'
            data['passwort'] = form.cleaned_data['passwort']
        data['ziel_db'] = form.cleaned_data['host_name'] + '\\' + form.cleaned_data['instance_name'] + ' - ' + form.cleaned_data['db_name']
        if 'dev' in form.cleaned_data['server']:
            data['umgebung_dev'] = form.cleaned_data['u_name']
            self.umgebung_anlegen(self.conf['dba']['lde']['dev'], form)
        if 'beta' in form.cleaned_data['server']:
            data['umgebung_beta'] = form.cleaned_data['u_name']
            self.umgebung_anlegen(self.conf['dba']['lde']['beta'], form)
        if 'release' in form.cleaned_data['server']:
            data['umgebung_release'] = form.cleaned_data['u_name']
            self.umgebung_anlegen(self.conf['dba']['lde']['release'], form)
        data['createuser'] = ''.join(["%0.2x" % int(x) for x in self.request.user.objid])
        data['createtime'] = int(datetime.now().timestamp())
        #print(data)
        id = mysql.write_data_single(dbt, 'Datenbank', data)
        self.success_url += '/'+str(id)
        return super(NewDBView, self).form_valid(form)

    def umgebung_anlegen(self, db_file_name, form):
        lde_db = sqlite.create(db_file_name)
        umgebung = sqlite.write_data_single(lde_db, 'umgebung', {'umgebungs_name': form.cleaned_data['u_name']})
        db = sqlite.query(lde_db, 'copy', [umgebung, 316], commit=True)

        update = { 'conf_value': form.cleaned_data['host_name'] + '\\' + form.cleaned_data['instance_name']}
        sqlite.update(lde_db, 'lde_conf', {'ind_umgebung': umgebung, 'conf_int_name': 'tmp_db_host'}, update)
        
        update = { 'conf_value': form.cleaned_data['db_name']}
        sqlite.update(lde_db, 'lde_conf', {'ind_umgebung': umgebung, 'conf_int_name': 'tablespace'}, update)
        
        update = { 'conf_value': form.cleaned_data['kunden_name'].lower()}
        sqlite.update(lde_db, 'lde_conf', {'ind_umgebung': umgebung, 'conf_int_name': 'kassenSchnittstelle'}, update)

        update = { 'conf_value': 'L:\\Dokumente\\_' + form.cleaned_data['kunden_name'].lower() + '\\'}
        sqlite.update(lde_db, 'lde_conf', {'ind_umgebung': umgebung, 'conf_int_name': 'dok_dir_client'}, update)

    def form_invalid(self, form):
        return super(NewDBView, self).form_invalid(form)

    def get_initial(self):
        initial = super(NewDBView, self).get_initial()
        initial.update(get_default_data())
        initial['seite'] = 'Neue Datenbank'
        initial['host_name'] = self.kwargs['host']
        initial['instance_name'] = self.kwargs['instance']
        #initial['form'] = self.form_class(self.kwargs)
        initial['backlink'] = '/dba/'
        initial['host_driver'] = [x for x in self.conf['dba']['database']['hosts'] if initial['host_name'] in x.values()][0]['driver']
        return initial
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_default_data())
        context['seite'] = 'Neue Datenbank'
        context['host_name'] = self.kwargs['host']
        context['instance_name'] = self.kwargs['instance']
        #context['form'] = self.form_class(self.kwargs)
        context['backlink'] = '/dba/'
        context['host_driver'] = [x for x in self.conf['dba']['database']['hosts'] if context['host_name'] in x.values()][0]['driver']
        return context

class NewDBSuccess(generic.TemplateView):
    template_name = 'dba/new_success.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_default_data())
        context['seite'] = 'Neue Datenbank'
        return context

class DbListView(generic.FormView):
    template_name = 'dba/index.html'
    conf = config(settings.DBA_CONFIG_FILE)
    seite = 'Übersicht'

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            settings.LOGIN_REDIRECT_URL = '/dba'
            return redirect('login')
        if not request.user.is_dsb and not request.user.is_superuser and not request.user.is_gf:
            print('user error')
            return redirect('passwd:index')
        dblist = DbListApp(self.conf)
        host_list = dblist.get_hosts()
        context = get_default_data()
        context['seite'] = self.seite
        context['host_list'] = host_list
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            print('user error')
            settings.LOGIN_REDIRECT_URL = '/dba'
            return redirect('login')
        dblist = DbListApp(self.conf)
        host = request.POST.get('hosts')
        instance = request.POST.get('instances')
        host_list = dblist.get_hosts(host)
        context = get_default_data()
        context['host_list'] = host_list
        context['host_name'] = dblist.host_name
        context['instance_list'] = dblist.get_instance_list(host, instance)
        context['instance_name'] = dblist.instance_name
        if dblist.host_name is None:
            return render(request, self.template_name, context)
        show_list = True
        if (request.POST.get('drop')):
            print('delete ' + request.POST.get('db_name'))
            connection = dblist.get_db_connection()
            dblist.db.drop(connection, request.POST.get('db_name'))
            show_list = True
        if (request.POST.get('shrink')):
            connection = dblist.get_db_connection()
            dblist.db.query(connection, 'shrink', request.POST.get('db_name'))
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

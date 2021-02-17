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
from src.db import mysql, sqlite, mssql


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
        ldap_user = ''.join(["%0.2x" % int(x) for x in self.request.user.objid])
        # DBT Datenbank Eintrag
        data = {}
        data['kunden_id'] = form.cleaned_data['kunden']
        data['grund_id'] = 3
        data['eingespielt_von'] = ''.join(["%0.2x" % int(x) for x in self.request.user.objid])
        data['eingespielt_am'] = int(datetime.now().timestamp())
        if form.cleaned_data['passwort'] != '':
            form.cleaned_data['verschluesselt'] = 'j'
            data['passwort'] = form.cleaned_data['passwort']
        data['ziel_db'] = form.cleaned_data['host_name']
        if form.cleaned_data['host_driver'].upper() != 'MYSQL':
            data['ziel_db'] += '\\' + form.cleaned_data['instance_name']     
        data['ziel_db'] += ' - ' + form.cleaned_data['db_name']
        if 'dev' in form.cleaned_data['server']:
            data['umgebung_dev'] = form.cleaned_data['u_name']
            self.umgebung_anlegen(self.conf['dba']['lde']['dev'], 545, form)
        if 'beta' in form.cleaned_data['server']:
            data['umgebung_beta'] = form.cleaned_data['u_name']
            self.umgebung_anlegen(self.conf['dba']['lde']['beta'], 472, form)
        if 'release' in form.cleaned_data['server']:
            data['umgebung_release'] = form.cleaned_data['u_name']
            self.umgebung_anlegen(self.conf['dba']['lde']['release'], 203, form)
        data['createuser'] = ldap_user
        data['createtime'] = int(datetime.now().timestamp())
        data['geplante_vern_am'] = int(datetime.now().timestamp()) + (14*86400)
        data['tatsaechliche_vern_am'] = 0
        data['rueckmeldung_kunde_am'] = 0
        data['ruecksendung_am'] = 0
        data['bereitgestellt_am'] = int(datetime.now().timestamp())
        id = mysql.write_data_single(dbt, 'Datenbank', data)
        # DBT Historie Eintrag
        hist = {}
        hist['kunde'] = form.cleaned_data['kunden']
        hist['datenbank'] = id
        hist['alt'] = ''
        hist['neu'] = ''
        hist['aenderungsgrund'] = 'Neuanlage'
        hist['zusammenfassung'] = ''
        hist['benutzer'] = ldap_user
        hist['aenderungszeit'] = int(datetime.now().timestamp())
        mysql.write_data_single(dbt, 'Historie', hist)
        self.import_db(form.cleaned_data)
        self.success_url += '/'+str(id)
        return super(NewDBView, self).form_valid(form)

    def umgebung_anlegen(self, db_file_name, id, form):
        lde_db = sqlite.create(db_file_name)
        umgebung = sqlite.write_data_single(lde_db, 'umgebung', {'umgebungs_name': form.cleaned_data['u_name']})
        db = sqlite.query(lde_db, 'copy', [umgebung, id], commit=True)

        if form.cleaned_data['host_driver'].upper() == 'MYSQL':
            update = { 'conf_value': form.cleaned_data['host_name']}
        else:
            update = { 'conf_value': form.cleaned_data['host_name'] + '\\' + form.cleaned_data['instance_name']}
        sqlite.update(lde_db, 'lde_conf', {'ind_umgebung': umgebung, 'conf_int_name': 'tmp_db_host'}, update)
        
        update = { 'conf_value': form.cleaned_data['db_name']}
        sqlite.update(lde_db, 'lde_conf', {'ind_umgebung': umgebung, 'conf_int_name': 'tablespace'}, update)

        update = { 'conf_value': form.cleaned_data['host_driver'].upper()}
        sqlite.update(lde_db, 'lde_conf', {'ind_umgebung': umgebung, 'conf_int_name': 'tmp_database_type'}, update)
        
        if form.cleaned_data['host_driver'].upper() == 'ORACLE':
            update = { 'conf_value': form.cleaned_data['db_name'].lower()}
            sqlite.update(lde_db, 'lde_conf', {'ind_umgebung': umgebung, 'conf_int_name': 'db_user'}, update)
        if form.cleaned_data['host_driver'].upper() == 'MYSQL':
            update = { 'conf_value': 'root'}
            sqlite.update(lde_db, 'lde_conf', {'ind_umgebung': umgebung, 'conf_int_name': 'db_user'}, update)
        
        update = { 'conf_value': form.cleaned_data['kunden_name'].lower()}
        sqlite.update(lde_db, 'lde_conf', {'ind_umgebung': umgebung, 'conf_int_name': 'kassenSchnittstelle'}, update)

        update = { 'conf_value': 'L:\\Dokumente\\_' + form.cleaned_data['kunden_name'].lower() + '\\'}
        sqlite.update(lde_db, 'lde_conf', {'ind_umgebung': umgebung, 'conf_int_name': 'dok_dir_client'}, update)

    def import_db(self, data):
        dblist = DbListApp(self.conf)
        dblist.host_name = data['host_name']
        dblist.driver = data['host_driver']
        dblist.instance_name = data['instance_name']
        connection = dblist.get_db_connection()
        data['filename'] = data['quellen'].split('\\')[-1]
        dblist.db.import_db(connection, data)
        

    def form_invalid(self, form):
        return super(NewDBView, self).form_invalid(form)

    def get_initial(self):
        initial = super(NewDBView, self).get_initial()
        initial.update(get_default_data())
        initial['seite'] = 'Neue Datenbank'
        host_name = self.kwargs['host']
        initial['instance_name'] = self.kwargs['instance']
        #initial['form'] = self.form_class(self.kwargs)
        initial['backlink'] = '/dba/'
        initial['host_driver'] = [x for x in self.conf['dba']['database']['hosts'] if host_name in x.values()][0]['driver']
        initial['host_name'] = [x for x in self.conf['dba']['database']['hosts'] if host_name in x.values()][0]['fqdn']
        return initial
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_default_data())
        context['seite'] = 'Neue Datenbank'
        host_name = self.kwargs['host']
        context['instance_name'] = self.kwargs['instance']
        #context['form'] = self.form_class(self.kwargs)
        context['backlink'] = '/dba/'
        context['host_driver'] = [x for x in self.conf['dba']['database']['hosts'] if host_name in x.values()][0]['driver']
        context['host_name'] = [x for x in self.conf['dba']['database']['hosts'] if host_name in x.values()][0]['fqdn']
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
        if (request.POST.get('remove_env')):
            dev_id = request.POST.get('devid')
            beta_id = request.POST.get('betaid')
            release_id = request.POST.get('releaseid')
            envid = request.POST.get('envid')
            envserver = request.POST.get('envserver')
            if dev_id and beta_id and release_id:
                if dev_id > 0:
                    general.umgebung_loeschen(self.conf, 'dev', dev_id)
                if beta_id > 0:
                    general.umgebung_loeschen(self.conf, 'beta', beta_id)
                if release_id > 0:
                    general.umgebung_loeschen(self.conf, 'release', release_id)
            if envid and envserver:
                general.umgebung_loeschen(self.conf, envserver, envid)
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
            print('show')
            context['seite'] = self.seite
            zeug = self.suchen(dblist)
            context['db_list'] = zeug[0]
            context['env_list'] = zeug[1]
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
        found_dev = []
        found_beta = []
        found_release = []
        for db in db_tuples:
            items = {}
            info = general.find_in_dbt(vernichten, dblist.instance_name, db[0])
            env_dev = general.umgebung_suchen(dev, db[0])
            env_beta = general.umgebung_suchen(beta, db[0])
            env_release = general.umgebung_suchen(release, db[0])
            items['umgebung'] = 'DEV: ' + env_dev[0][0]
            items['umgebung'] += "\r\n" + 'BETA: ' + env_beta[0][0]
            items['umgebung'] += "\r\n" + 'RELEASE: ' + env_release[0][0]
            items['devid'] = env_dev[0][1]
            for env in env_dev:
                found_dev.append(env[1])
            items['betaid'] = env_beta[0][1]
            for env in env_beta:
                found_beta.append(env[1])
            items['releaseid'] = env_release[0][1]
            for env in env_release:
                found_release.append(env[1])
            items['name'] = db[0]
            items['size'] = db[1]
            items['log'] = db[2]
            items['sum'] = db[3]
            items['add'] = db[4]
            if info:
                if info[0] is None:
                    items['delete'] = date.fromtimestamp(0)
                else:
                    items['delete'] = date.fromtimestamp(info[0])
                items['dbtid'] = info[2]
                items['delta'] = (items['delete'] - date.today()).days
            else:
                items['delete'] = 'nicht gefunden'
                items['delta'] = -9000
            db_list.append(items)
        unused = []
        for env in dev:
            if env[2] not in found_dev:
                i = {'name': env[1].decode("cp1252"), 'id': env[2], 'server': 'dev'}
                unused.append(i)
        for env in beta:
            if env[2] not in found_beta:
                i = {'name': env[1].decode("cp1252"), 'id': env[2], 'server': 'beta'}
                unused.append(i)
        for env in release:
            if env[2] not in found_release:
                i = {'name': env[1].decode("cp1252"), 'id': env[2], 'server': 'release'}
                unused.append(i)
        return (db_list, unused)

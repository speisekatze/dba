import os
from django.conf import settings
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit
from django import forms
from src.config import config
from src.db import mysql
from dba.app import general
import traceback

class SucheForm(forms.Form):

    def __init__(self, host_list, *args, **kwargs):
        super(SucheForm, self).__init__(*args, **kwargs)
        hosts = []
        for host in host_list:
            hosts.append((host['name'], host['fqdn']))

        self.fields['hosts'] = forms.ChoiceField(choices=hosts)


class NewDbForm(forms.Form):
    conf = config(settings.DBA_CONFIG_FILE)
    db_name = forms.CharField(label='Datenbankname')
    u_name = forms.CharField(label='Umgebung')
    server = forms.MultipleChoiceField(label='Server',
                               choices=[('dev', 'DEV'), ('beta', 'BETA'), ('release', 'RELEASE')],
                               widget=forms.CheckboxSelectMultiple)
    kunden = forms.ChoiceField(label='Kunden')
    quellen = forms.ChoiceField(label='Quellen', widget=forms.RadioSelect)
    passwort = forms.CharField(label='Passwort zum Entpacken', required=False)
    host_name = forms.CharField(widget=forms.HiddenInput())
    instance_name = forms.CharField(widget=forms.HiddenInput())
    kunden_name = forms.CharField(widget=forms.HiddenInput())
    host_driver = forms.CharField(widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super(NewDbForm, self).__init__(*args, **kwargs)
        dbt = general.connect_dbt(self.conf)
        kunden = mysql.query(dbt, 'get_kunden')
        k = [(0, 'Bitte auswählen')]
        for kunde in kunden:
            k.append((kunde[0], kunde[1]))
        self.fields['kunden'].choices = k
        filenames = []
        instance = ''
        if 'initial' in kwargs:
            instance = kwargs['initial']['instance_name']
        if len(args) > 0:
            instance = args[0]['instance']
        for root, d_names, f_names in os.walk(self.conf['dba']['dump']+instance+'\\'):
            for f in f_names:
                fname = os.path.join(root, f).replace('/', '\\')
                filenames.append((fname, fname))
        self.fields['quellen'].choices = filenames

        self.helper = FormHelper
        self.helper.form_method = 'post'
        self.helper.form_style = 'inline'
        self.helper.label_class = 'left'
        self.helper.field_class = 'left'
        self.helper.field_template = 'field.html'
        self.helper.use_custom_control = True
        self.helper.layout = Layout(
            Fieldset(
                'Informationen',
                'db_name',
                'u_name',
                'server',
                'kunden',
                'passwort',
                'quellen',
                'host_name',
                'instance_name',
                'kunden_name',
                'host_driver',
            ),
            ButtonHolder(
                Submit('submit', 'Senden')
            )
        )

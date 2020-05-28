import os
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit
from django import forms
from src.config import config
from src.db import mysql
from dba.app import general


class SucheForm(forms.Form):

    def __init__(self, host_list, *args, **kwargs):
        super(SucheForm, self).__init__(*args, **kwargs)
        hosts = []
        for host in host_list:
            hosts.append((host['name'], host['fqdn']))

        self.fields['hosts'] = forms.ChoiceField(choices=hosts)


class NewDbForm(forms.Form):
    conf = config('config/config.yml')
    db_name = forms.CharField(label='Datenbankname')
    u_name = forms.CharField(label='Umgebung')
    server = forms.ChoiceField(label='Server',
                               choices=[('dev', 'DEV'), ('beta', 'BETA'), ('release', 'RELEASE')],
                               widget=forms.CheckboxSelectMultiple)
    kunden = forms.ChoiceField(label='Kunden')
    quellen = forms.ChoiceField(label='Quellen', widget=forms.RadioSelect)
    passwort = forms.CharField(label='Passwort zum Entpacken')

    def __init__(self, *args, **kwargs):
        super(NewDbForm, self).__init__(*args, **kwargs)
        dbt = general.connect_dbt(self.conf)
        kunden = mysql.query(dbt, 'get_kunden')
        k = []
        for kunde in kunden:
            k.append((kunde[0], kunde[1]))
        self.fields['kunden'].choices = k
        filenames = []
        for root, d_names, f_names in os.walk(self.conf['dba']['dump']):
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
        self.helper.layout = Layout(
            Fieldset(
                'Informationen',
                'db_name',
                'u_name',
                'server',
                'kunden',
                'passwort',
                'quellen',
            ),
            ButtonHolder(
                Submit('submit', 'Senden')
            )
        )

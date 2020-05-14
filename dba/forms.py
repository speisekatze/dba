from django import forms


class SucheForm(forms.Form):

    def __init__(self, host_list, *args, **kwargs):
        super(SucheForm, self).__init__(*args, **kwargs)
        hosts = []
        for host in host_list:
            hosts.append((host['name'], host['fqdn']))

        self.fields['hosts'] = forms.ChoiceField(choices=hosts)

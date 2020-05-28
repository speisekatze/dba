import os
from django.conf import settings
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit
from django import forms


class PasswdForm(forms.Form):
    laenge = forms.CharField(label="Länge")
    filler = forms.CharField(label="Füllzeichen")
    typ = forms.ChoiceField(label="Typ", choices=[('words', 'Wörter'), ('chars', 'Zeichen')])

    def __init__(self, *args, **kwargs):
        super(PasswdForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper
        self.helper.form_method = 'post'
        self.helper.form_style = 'inline'
        self.helper.label_class = 'left'
        self.helper.field_class = 'left'
        self.helper.field_template = 'field.html'
        self.helper.layout = Layout(
            Fieldset(
                'Einstellungen',
                'typ',
                'laenge',
                'filler',
            ButtonHolder(
                Submit('submit', 'Senden')
            )
            ),

        )

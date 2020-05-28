from django.shortcuts import render
from django.views.generic import FormView
from .forms import PasswdForm


def get_default_data():
    data = {}
    data['headline'] = 'Passwort Generator'
    return data

# Create your views here.
class PasswdView(FormView):
    template_name = 'passwd/index.html'
    seite = 'Passwörter'
    form_class = PasswdForm

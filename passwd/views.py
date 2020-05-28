import random
from django.conf import settings
from django.shortcuts import render
from django.views.generic import FormView
from .forms import PasswdForm


def get_default_data():
    data = {}
    data['headline'] = 'Passwort Generator'
    return data


def words(laenge, anzahl, filler):
    passwds = ''
    if laenge < 2:
        laenge = abs(laenge) + 2
    for _ in range(0, anzahl):
        pw = []
        for _ in range(0, laenge):
            with open(settings.PASSWD_WORD_FILE) as f:
                lines = f.readlines()
                pw.append(random.choice(lines).rstrip("\n").rstrip("\r"))
        passwds += filler[0].join(pw) + "\r\n"
    return passwds


def chars(laenge, anzahl):
    passwds = ''
    up = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    low = up.lower()
    digi = '0123456789'
    special = '$§%&()=?+*-_#'
    if laenge < 12:
        laenge = abs(laenge) + 12
    for _ in range(0, anzahl):
        pw = []
        for i in range(0, laenge):
            if i == 0:
                pw.append(random.choice(up))
            elif i < (laenge/2):
                pw.append(random.choice(up+low+digi))
            elif i > (laenge/2):
                pw.append(random.choice(special+low+digi))
            else:
                pw.append(random.choice(special))
        passwds += ''.join(pw) + "\r\n"
    return passwds


# Create your views here.
class PasswdView(FormView):
    template_name = 'passwd/index.html'
    seite = 'Einstellungen'
    form_class = PasswdForm
    success_url = 'ergebniss'

    def __init__(self, *args, **kwargs):
        super(PasswdView, self).__init__(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_default_data())
        print(self.seite)
        context['seite'] = self.seite
        return context

    def post(self, request, *args, **kwargs):
        context = get_default_data()
        context['seite'] = 'Passwörter'
        context['form'] = self.form_class(initial=self.get_initial())
        anzahl = int(request.POST.get('count'))
        laenge = int(request.POST.get('laenge'))
        typ = request.POST.get('typ')
        filler = request.POST.get('filler')
        if typ == 'words':
            context['passwds'] = words(laenge, anzahl, filler)
        else:
            context['passwds'] = chars(laenge, anzahl)
        return render(request, self.template_name, context)

    def get_initial(self):
        initial = super(PasswdView, self).get_initial()
        initial.update({'filler': '-'})
        initial.update({'laenge': '4'})
        initial.update({'count': '5'})
        initial.update({'typ': 'words'})
        return initial

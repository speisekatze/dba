# from django.shortcuts import get_object_or_404, render
# from django.urls import reverse
from django.views import generic


# Create your views here.
def get_default_data():
    data = {}
    data['headline'] = 'Datenbank Admin'
    return data


class IndexView(generic.TemplateView):
    template_name = 'dba/index.html'
    context_object_name = 'latest_question_list'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_default_data())
        context['seite'] = 'Übersicht'
        return context

from django.shortcuts import render
from django.views import generic
from . import models
from django.shortcuts import get_object_or_404
import sys


class PostDetail(generic.TemplateView):
    def get_template_names(self):
        if self.klass == models.Drug:
            return 'prozdo_main/post/drug_detail.html'

    def get_object(self):
        if 'alias' in self.kwargs:
            alias = self.kwargs['alias']
            post = get_object_or_404(models.Post, alias=alias)
        else:
            pk = self.kwargs['pk']
            post = get_object_or_404(models.Post, pk=pk)
        self.post = post
        return self.post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['drug'] = self.get_object()
        return context

class DrugList(generic.ListView):
    template_name = 'prozdo_main/post/drug_list.html'
    model = models.Drug
    context_object_name = 'drugs'


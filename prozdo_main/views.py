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
            alias_text = self.kwargs['alias']
            alias = get_object_or_404(models.Alias, alias=alias_text)
            klass = getattr(sys.modules['prozdo_main'].models, alias.post_cls)
            ob = klass.objects.get(pk=alias.post_id)
            self.klass = klass
        elif 'pk' in self.kwargs:
            klass = getattr(sys.modules['prozdo_main'].models, self.kwargs['klass'])
            ob = klass.objects.get(pk=self.kwargs['pk'])
            self.klass = klass
        return ob

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['drug'] = self.get_object()
        return context

class DrugList(generic.ListView):
    template_name = 'prozdo_main/post/drug_list.html'
    model = models.Drug
    context_object_name = 'drugs'


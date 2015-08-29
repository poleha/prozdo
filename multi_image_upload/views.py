from django.shortcuts import render

class ModelImageMixin:
    image_formset = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['image_formset'] = self.image_formset(instance=self.object)
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        post = form.instance
        image_formset = self.image_formset(self.request.POST, self.request.FILES, instance=post)
        if image_formset.is_valid():
                image_formset.save()
        return response

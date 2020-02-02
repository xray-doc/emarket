from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseRedirect
from django.shortcuts import reverse
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormMixin

from comments.forms import CommentForm
from comments.models import Comment
from .models import Product


class ProductDetailView(FormMixin, DetailView):

    template_name   = 'products/product_detail.html'
    form_class      = CommentForm
    model           = Product

    def get_initial(self):
        initial = super().get_initial()

        # Hidden fields of the form contain content type of a Product model
        # and object id of a particular product.
        initial['content_type'] = self.object.get_content_type
        initial['object_id'] = self.object.id
        return initial

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form, *args, **kwargs):
        if not self.request.user.is_authenticated():
            return HttpResponseRedirect(reverse('accounts:login'))

        c_type = form.cleaned_data.get("content_type").lower()
        content_type = ContentType.objects.get(model=c_type)
        object_id = form.cleaned_data.get('object_id')
        content = form.cleaned_data.get("content")
        try:
            parent_id = int(self.request.POST.get("parent_id"))
            parent_obj = Comment.objects.get(id=parent_id)
        except:
            parent_obj = None

        new_comment, created = Comment.objects.get_or_create(
            user=self.request.user,
            content_type=content_type,
            object_id=object_id,
            content=content,
            parent=parent_obj,
        )
        return super().form_valid(self, **kwargs)

    def get_success_url(self):
        return self.object.get_absolute_url()

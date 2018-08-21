from django.core.mail import send_mail, BadHeaderError
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views.generic.list import ListView
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
from django.urls import reverse

from products.models import *
from .forms import *


class MainView(ListView):

    model = Product
    template_name = 'home.html'
    fields = [
        'os',
        'diagonal',
        'ram',
        'processor'
    ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Here we get distinct values of columns from Product model
        # in order to create choices for filter widgets.
        for field in self.fields:
            # TODO: release next method in model:
            distinct_qs = Product.objects.all().values_list(field).distinct()
            choices = []
            for i in list(distinct_qs):
                key = field + '__' + str(i[0])
                val = i[0]
                choices.append({'key': key, 'val': val})
            key = field + '_select'
            context[key] = choices
        return context


class FilteredProductsView(ListView):

    model = Product
    template_name = 'products_on_main_page.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # all the Q filteration arguments collects in the filters dict and
        # extracts to query at the end
        filters = {}
        for filter_key in self.request.GET.keys():
            if filter_key == 'csrfmiddlewaretoken': continue
            if filter_key == 'search':
                q = self.request.GET.get(filter_key)
                filters['search'] = Q(name__icontains=q) | \
                                    Q(short_description__icontains=q) | \
                                    Q(other_specifications__icontains=q)
                continue

            # Next:
            # os__android > ['os', 'android'].
            # BUT! Some specifications are like:
            # processor_select ['processor_name'],
            # so we need to get value from self.request in those cases
            key, val = filter_key.split('__')

            if key == 'os':
                if not filters.get('os'):
                    filters['os'] = Q(os=val)
                else:
                    # If more then one OS selected, we need all of them, not the only one.
                    filters['os'] = filters['os'] | Q(os=val)

            elif key == 'diagonal':
                if not filters.get('diagonal'):
                    filters['diagonal'] = Q(diagonal=val)
                else:
                    # If more then one diagonal selected, we need all of them, not the only one.
                    filters['diagonal'] = filters['diagonal'] | Q(diagonal=val)

            elif key == 'memory':
                num = self.request.GET.get(filter_key)
                if not num: continue
                if val == 'min':
                    filters['memory_min'] = Q(built_in_memory__gte=num)
                if val == 'max':
                    filters['memory_max'] = Q(built_in_memory__lte=num)

            elif key == 'ram':
                if not filters.get('ram'):
                    filters['ram'] = Q(ram=val)
                else:
                    # If more then one RAM selected, we need all of them, not the only one.
                    filters['ram'] = filters['ram'] | Q(ram=val)

            elif key == 'processor':
                processor_name = self.request.GET.get(filter_key)
                if not processor_name: continue
                filters['processor'] = Q(processor=processor_name)

            elif key == 'price':
                num = self.request.GET.get(filter_key)
                if not num: continue
                if val == 'min':
                    filters['price_min'] = Q(price__gte=num)
                if val == 'max':
                    filters['price_max'] = Q(price__lte=num)

        context['product_list'] = context['product_list'].filter(*filters.values())  # Final queryset of products to show
        return context


class DeliveryView(TemplateView):

    template_name = 'delivery.html'


class ContactsView(FormView):

    template_name = 'contacts.html'
    form_class = ContactForm
    # TODO: implement success page to redirect

    def get_success_url(self):
        return reverse('main')

    def form_valid(self, form):
        subject = form.cleaned_data['subject']
        sender = form.cleaned_data['sender']
        message = form.cleaned_data['message']
        message = "<-------contacts EMARKET------->\n\n" + message
        copy = form.cleaned_data['copy']

        recepients = ['m.nikolaev1@gmail.com']
        if copy:
            recepients.append(sender)
        try:
            send_mail(subject, message, 'm10040@mail.ru', recepients)
        except BadHeaderError:
            return HttpResponse('Invalid header found')
        return super().form_valid(form)




#TODO: make comments with mixer. At first, start with new commit and do it locally.

# This view used like a script for generating comments to
# products
# def forging_comments(request):
#     import random
#     from django.contrib.contenttypes.models import ContentType
#     from comments.models import Comment
#     from django.contrib.auth import (
#         authenticate,
#         get_user_model,
#         login,
#         logout,
#     )
#     User = get_user_model()
#
#     def create_users():
#         users_objects = []
#         users_data = [
#             ('Andrey', 'andrey', 'andr@andr.ru'),
#             ('Pavel', 'pavel', 'pav@pav.ru'),
#             ('Dmitriy', 'dima', 'dim@dim.ru'),
#             ('Alex', 'alex', 'alex@alex.ru')
#         ]
#
#         for user_data in users_data:
#             new_user = User(username=user_data[0], password=user_data[1], email=user_data[2])
#             try:
#                 new_user.save()
#             except:
#                 pass
#             users_objects.append(new_user)
#         return users_objects
#     new_users = create_users()
#
#     comments = [
#         'Great gadget',
#         "I've used it for a long time and can recommend it",
#         "That's a good tablet",
#         'I prefere that one',
#         "It's my comment"
#     ]
#
#     replies = [
#         'Agree with you',
#         "I don't think so",
#         '+1',
#         "you're right"
#     ]
#
#     product_content_type = ContentType.objects.get(model='product')
#     for product in Product.objects.all():
#         first_comment, created = Comment.objects.get_or_create(
#             user=random.choice(new_users),
#             content_type=product_content_type,
#             object_id=product.id,
#             content=random.choice(comments),
#             parent=None,
#         )
#
#         second_comment, created = Comment.objects.get_or_create(
#             user=random.choice(new_users),
#             content_type=product_content_type,
#             object_id=product.id,
#             content=random.choice(comments),
#             parent=None,
#         )
#
#         reply, created = Comment.objects.get_or_create(
#             user=random.choice(new_users),
#             content_type=product_content_type,
#             object_id=product.id,
#             content=random.choice(comments),
#             parent=second_comment,
#         )
#
#
#     return HttpResponse('brrrt')
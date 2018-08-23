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


class SuccessView(TemplateView):

    template_name = 'success.html'


class ContactsView(FormView):

    template_name = 'contacts.html'
    form_class = ContactForm

    def get_success_url(self):
        return reverse('success')

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

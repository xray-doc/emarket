from django.conf import settings
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView, FormMixin
from django.views.generic.list import ListView
from django.urls import reverse

from products.models import Product
from .forms import ContactForm, FilterForm


class MainView(ListView, FormMixin):
    model = Product
    template_name = 'emarket/home.html'
    form_class = FilterForm


class FilteredProductsView(FormView):
    template_name   = 'emarket/products_on_main_page.html'
    form_class      = FilterForm
    queryset        = Product.objects.all()

    def form_valid(self, form):
        prs = self.queryset
        data = form.cleaned_data

        oses = data['os']
        if oses: prs = prs.filter(os__in=oses)

        diagonals = data['diagonal']
        if diagonals: prs = prs.filter(diagonal__in=diagonals)

        processors = data['processor']
        if processors: prs = prs.filter(processor__in=processors)

        rams = data['ram']
        if rams: prs = prs.filter(ram__in=rams)

        mmin = data['memory_min']
        if mmin: prs = prs.filter(built_in_memory__gte=mmin)

        mmax = data['memory_max']
        if mmax: prs = prs.filter(built_in_memory__lte=mmax)

        minprice = data['min_price']
        if minprice and minprice > 0: prs = prs.filter(price__gte=minprice)

        maxprice = data['max_price']
        if maxprice and maxprice > 0: prs = prs.filter(price__lte=maxprice)

        search = data['search']
        if search: prs = prs.filter(name__icontains=search)

        return super().render_to_response({'product_list': prs})


class DeliveryView(TemplateView):
    template_name = 'emarket/delivery.html'


class SuccessView(TemplateView):
    template_name = 'emarket/success.html'


class ContactsView(FormView):
    template_name = 'emarket/contacts.html'
    form_class = ContactForm

    def get_success_url(self):
        return reverse('success')

    def form_valid(self, form):
        subject = form.cleaned_data['subject']
        sender = form.cleaned_data['sender']
        message = form.cleaned_data['message']
        message = f'''
Message from: {sender} 

{message} 
'''
        subject = '[Django Contacts] ' + subject
        copy = form.cleaned_data['copy']
        recepients = [settings.ADMINS[0][1]]
        if copy: recepients.append(sender)
        try:
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recepients)
        except BadHeaderError:
            return HttpResponse('Invalid header found')
        return super().form_valid(form)

from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic.list import ListView
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
from django.urls import reverse

from products.models import *
from .forms import ContactForm, FilterForm


class MainView(ListView):

    model = Product
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = FilterForm
        return context


class FilteredProductsView(FormView):

#TODO search field

    model = Product
    template_name = 'products_on_main_page.html'
    form_class = FilterForm

    def form_valid(self, form, *args, **kwargs):
        prs = Product.objects.all()

        oses = form.cleaned_data['os']
        if oses:
            prs = prs.filter(os__in=oses)

        diagonals = form.cleaned_data['diagonal']
        if diagonals:
            prs = prs.filter(diagonal__in=diagonals)

        processors = form.cleaned_data['processor']
        if processors:
            prs = prs.filter(processor__in=processors)

        rams = form.cleaned_data['ram']
        if rams:
            prs = prs.filter(ram__in=rams)

        mmin = form.cleaned_data['memory_min']
        if mmin:
            prs = prs.filter(built_in_memory__gte=mmin)

        mmax = form.cleaned_data['memory_max']
        if mmax:
            prs = prs.filter(built_in_memory__lte=mmax)

        minprice = form.cleaned_data['min_price']
        if minprice and minprice > 0:
            prs = prs.filter(price__gte=minprice)

        maxprice = form.cleaned_data['max_price']
        if maxprice and maxprice > 0:
            prs = prs.filter(price__lte=maxprice)

        context = {'product_list': prs}
        return render(self.request, self.template_name, context=context)

    def form_invalid(self, form):
        context = {'product_list': Product.objects.all()}

        return render(self.request, self.template_name, context=context)


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

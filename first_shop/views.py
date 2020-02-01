from django.core.mail import send_mail, BadHeaderError
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic.list import ListView
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView, FormMixin
from django.urls import reverse

from products.models import Product
from .forms import ContactForm, FilterForm


class MainView(ListView, FormMixin):
    model = Product
    template_name = 'home.html'
    form_class = FilterForm


class FilteredProductsView(ListView):

    model = Product
    template_name = 'products_on_main_page.html'
    form_class = FilterForm

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        prs = Product.objects.all()

        if form.is_valid():
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

            search = form.cleaned_data['search']
            if search:
                prs = prs.filter(name__icontains=search)

        context = {'product_list': prs}
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

        message = f'''
Message from: {sender} 

{message} 
'''
        subject = '[Django Contacts] ' + subject
        copy = form.cleaned_data['copy']

        recepients = [settings.ADMINS[0][1]]
        if copy:
            recepients.append(sender)
        try:
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recepients)
        except BadHeaderError:
            return HttpResponse('Invalid header found')
        return super().form_valid(form)

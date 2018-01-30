from django.shortcuts import render
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse, HttpResponseRedirect
from django.db.models import Q

from products.models import *
from .forms import *




def main(request):
    if request.method == 'POST':
        q = request.POST.get('search')
        queryset = Product.objects.filter(
            Q(name__icontains=q)|
            Q(short_description__icontains=q)|
            Q(description__icontains=q)
        )
        search_result = True
    else:
        queryset = Product.objects.all()
    #form = FilterProductForm(request.POST)

    def get_choices_from_field(field):
            distinct_qs = Product.objects.all().values_list(field).distinct()
            choices = [i[0] for i in list(distinct_qs)]  # [(2,), (4,)] > [(2,2), (4.4)]
            choices.sort()
            return choices

    os_select               = get_choices_from_field('os')
    diagonal_select         = get_choices_from_field('diagonal')
    ram_select              = get_choices_from_field('ram')
    processor_select        = get_choices_from_field('processor')
    #built_in_memory_select  =


    return render(request, 'home.html', locals())



def delivery(request):
    return render(request, 'delivery.html', locals())



def contacts(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            subject = form.cleaned_data['subject']
            sender = form.cleaned_data['sender']
            message = form.cleaned_data['message']
            message = "<-------контакты EMARKET------->\n\n" + message
            copy = form.cleaned_data['copy']

            recepients = ['m.nikolaev1@gmail.com']
            if copy:
                recepients.append(sender)
            try:
                send_mail(subject, message, 'm10040@mail.ru', recepients)
            except BadHeaderError:
                return HttpResponse('Invalid header found')
            return render(request, 'orders/done.html', locals())

    else:
        form = ContactForm()
    return render(request, 'contacts.html', {'form': form})
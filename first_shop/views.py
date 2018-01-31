from django.shortcuts import render
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse, HttpResponseRedirect
from django.db.models import Q

from products.models import *
from .forms import *




def main(request):
    qs = Product.objects.all()                   # queryset of all products


    # Filtration
    if request.method == 'POST':
        for filter_key in request.POST.keys():
            if filter_key == 'csrfmiddlewaretoken': continue
            if filter_key == 'search':
                q = request.POST.get(filter_key)
                qs = qs.filter(
                    Q(name__icontains=q)|
                    Q(short_description__icontains=q)|
                    Q(description__icontains=q)
                )

            key, val = filter_key.split('__')     # os__android > ['os', 'android'].
                                                  # BUT! Some specifications comes like:
            if key == 'os':                       # processor_select ['processor_name'],
                qs = qs.filter(os=val)            # so we need to get value from request

            if key == 'diagonal':
                qs = qs.filter(diagonal=val)

            if key == 'memory':
                num = request.POST.get(filter_key)
                if not num: continue
                if val == 'min':
                    qs = qs.filter(built_in_memory__gte=num)
                if val == 'max':
                    qs = qs.filter(built_in_memory__lte=num)

            if key == 'ram':
                qs = qs.filter(ram=val)

            if key == 'pocessor':
                processor_name = request.POST.get(filter_key)
                qs = qs.filter(processor=processor_name)

            if key == 'price':
                num = request.POST.get(filter_key)
                if not num: continue
                if val == 'min':
                    qs = qs.filter(price__gte=num)
                if val == 'max':
                    qs = qs.filter(price__lte=num)

    def get_choices_from_field(field):
        """
        Get distinct values from field in model.
        Needs for creating choices for filter widgets.
        :param field: field in model to create choices from.
        :return: [{'field__val': 'val'},]
        """
        distinct_qs = Product.objects.all().values_list(field).distinct()
        choices = []
        for i in list(distinct_qs):
            key = field + '__' + str(i[0])
            val = i[0]
            choices.append({'key': key, 'val': val})

        # choices = [field + '__' + str(i[0]) for i in list(distinct_qs)]  # [(2,), (4,)] > [(2,2), (4.4)]
        # choices.sort()
        return choices

    os_select         = get_choices_from_field('os')
    diagonal_select   = get_choices_from_field('diagonal')
    ram_select        = get_choices_from_field('ram')
    processor_select  = get_choices_from_field('processor')

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
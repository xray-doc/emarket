from django.shortcuts import render
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse, HttpResponseRedirect
from django.db.models import Q

from products.models import *
from .forms import *




def main(request):
    qs = Product.objects.all()                   # queryset of all products

    # Creating filter form
    def get_choices_from_column(column):
        """
        Get distinct values of column in model.
        Is used for creating choices for filter widgets.
        :param column: column in model to create choices from.
        :return: [{'column__val': 'val'},]
        """
        distinct_qs = Product.objects.all().values_list(column).distinct()
        choices = []
        for i in list(distinct_qs):
            key = column + '__' + str(i[0])
            val = i[0]
            choices.append({'key': key, 'val': val})

        # choices = [field + '__' + str(i[0]) for i in list(distinct_qs)]  # [(2,), (4,)] > [(2,2), (4.4)]
        # choices.sort()
        return choices

    os_select         = get_choices_from_column('os')
    diagonal_select   = get_choices_from_column('diagonal')
    ram_select        = get_choices_from_column('ram')
    processor_select  = get_choices_from_column('processor')

    return render(request, 'home.html', locals())


def filteredProducts(request):
    qs = Product.objects.all()
    # Filtration
    if request.method == 'POST':

        # all the Q filteration arguments collects in the filters dict and
        # extracts to query at the end
        filters = {}
        for filter_key in request.POST.keys():
            if filter_key == 'csrfmiddlewaretoken': continue
            if filter_key == 'search':
                q = request.POST.get(filter_key)
                filters['search'] = Q(name__icontains=q) | \
                                    Q(short_description__icontains=q) | \
                                    Q(other_specifications__icontains=q)
                continue

            # Next:
            # os__android > ['os', 'android'].
            # BUT! Some specifications comes like:
            # processor_select ['processor_name'],
            # so we need to get value from request in those cases
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
                num = request.POST.get(filter_key)
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
                processor_name = request.POST.get(filter_key)
                if not processor_name: continue
                filters['processor'] = Q(processor=processor_name)
            elif key == 'price':
                num = request.POST.get(filter_key)
                if not num: continue
                if val == 'min':
                    filters['price_min'] = Q(price__gte=num)
                if val == 'max':
                    filters['price_max'] = Q(price__lte=num)

        qs = qs.filter(*filters.values())  # Final queryset of products to show
    return render(request, 'products_on_main_page.html', {'qs': qs})


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
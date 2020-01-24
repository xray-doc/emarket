from django import forms
from django.db.models import Max, Min
from products.models import Product


class ContactForm(forms.Form):
    subject = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'size': '40', 'class': 'form-control'}))
    sender = forms.EmailField(widget=forms.TextInput(attrs={'size': '40', 'class': 'form-control'}))
    message = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control'}))
    copy = forms.BooleanField(required=False)


def get_field_choices(field):
    val = Product.get_distinct_values_from_field(field)
    return ((v[0], v[0]) for v in val)


class FilterForm(forms.Form):

    maxprice = Product.objects.aggregate(max=Max('price'))['max']
    minprice = Product.objects.aggregate(min=Min('price'))['min']
    maxmemory = Product.objects.aggregate(max=Max('built_in_memory'))['max']
    minmemory = Product.objects.aggregate(min=Min('built_in_memory'))['min']

    os = forms.MultipleChoiceField(
        choices=get_field_choices('os'),
        widget=forms.CheckboxSelectMultiple(),
        required=False
    )
    diagonal = forms.MultipleChoiceField(
        choices=get_field_choices('diagonal'),
        widget = forms.CheckboxSelectMultiple(),
        required = False
    )
    processor = forms.MultipleChoiceField(
        choices=get_field_choices('processor'),
        widget=forms.CheckboxSelectMultiple(),
        required=False
    )
    ram = forms.MultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple(),
        choices=get_field_choices('ram')
    )
    memory_min = forms.IntegerField(
        required=False,
        initial=minmemory,
        max_value=9999,
        min_value=0
    )
    memory_max = forms.IntegerField(
        required=False,
        initial=maxmemory,
        max_value=9999,
        min_value=0
    )
    min_price = forms.IntegerField(required=False,
                                   label='Min price: ' + str(minprice) + ' RUB',
                                   initial=minprice,
                                   widget=forms.NumberInput(attrs={'type': 'range',
                                                                   'min': minprice,
                                                                   'id': 'mprice',
                                                                   'max': maxprice,
                                                                   'oninput': 'printprice("mprice")'}))

    max_price = forms.IntegerField(required=False,
                                   label='Max price: ' + str(maxprice) + ' RUB',
                                   initial=maxprice,
                                   widget=forms.NumberInput(attrs={'type': 'range',
                                                                   'min': minprice,
                                                                   'id': 'maxprice',
                                                                   'max': maxprice,
                                                                   'oninput': 'printprice("maxprice")'}))

from django import forms
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
    """
    Filter form from the home page.
    """

    os = forms.MultipleChoiceField(
        choices=lambda: get_field_choices('os'),
        widget=forms.CheckboxSelectMultiple(),
        required=False
    )
    diagonal = forms.MultipleChoiceField(
        choices=lambda: get_field_choices('diagonal'),
        widget = forms.CheckboxSelectMultiple(),
        required = False
    )
    processor = forms.MultipleChoiceField(
        choices=lambda: get_field_choices('processor'),
        widget=forms.CheckboxSelectMultiple(),
        required=False
    )
    ram = forms.MultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple(),
        choices=lambda: get_field_choices('ram')
    )
    memory_min = forms.IntegerField(
        required=False,
        initial=lambda: Product.get_min_memory(),
        max_value=9999,
        min_value=0
    )
    memory_max = forms.IntegerField(
        required=False,
        initial=lambda: Product.get_max_memory(),
        max_value=9999,
        min_value=0
    )
    min_price = forms.IntegerField(required=False,
                                   label='Min price: ' + str(Product.get_min_price()) + ' RUB',
                                   initial=lambda: Product.get_min_price(),
                                   widget=forms.NumberInput(attrs={'type': 'range',
                                                                   'min': lambda: Product.get_min_price(),
                                                                   'id': 'mprice',
                                                                   'max': lambda: Product.get_max_price(),
                                                                   'oninput': 'printprice("mprice")'}))

    max_price = forms.IntegerField(required=False,
                                   label='Max price: ' + str(Product.get_max_price()) + ' RUB',
                                   initial=lambda: Product.get_max_price(),
                                   widget=forms.NumberInput(attrs={'type': 'range',
                                                                   'min': lambda: Product.get_min_price(),
                                                                   'id': 'maxprice',
                                                                   'max': lambda: Product.get_max_price(),
                                                                   'oninput': 'printprice("maxprice")'}))

    search = forms.CharField(required=False,
                             max_length=200,
                             widget=forms.HiddenInput())


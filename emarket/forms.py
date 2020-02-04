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
    fields_with_choices = [
        'os',
        'diagonal',
        'processor',
        'ram'
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Creating choices for every field
        for field in self.fields_with_choices:
            self.fields[field].choices = get_field_choices(field)

        # Fields in the filter are not required
        for field in self.fields.keys():
            self.fields[field].required = False

    os          = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple())
    diagonal    = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple())
    processor   = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple())
    ram         = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple())

    memory_min  = forms.IntegerField(
        initial=Product.get_min_memory,
        max_value=9999,
        min_value=0
    )
    memory_max = forms.IntegerField(
        initial=Product.get_max_memory,
        max_value=9999,
        min_value=0
    )
    min_price = forms.IntegerField(label='Min price: ' + str(Product.get_min_price()) + ' RUB',
                                   initial=Product.get_min_price,
                                   widget=forms.NumberInput(attrs={'type': 'range',
                                                                   'min': Product.get_min_price,
                                                                   'id': 'mprice',
                                                                   'max': Product.get_max_price,
                                                                   'oninput': 'printprice("mprice")'}))

    max_price = forms.IntegerField(label='Max price: ' + str(Product.get_max_price()) + ' RUB',
                                   initial=Product.get_max_price,
                                   widget=forms.NumberInput(attrs={'type': 'range',
                                                                   'min': Product.get_min_price,
                                                                   'id': 'maxprice',
                                                                   'max': Product.get_max_price,
                                                                   'oninput': 'printprice("maxprice")'}))

    search = forms.CharField(max_length=200, widget=forms.HiddenInput())


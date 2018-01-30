from django import forms
from products.models import Product

class ContactForm(forms.Form):
    subject = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'size': '40', 'class': 'form-control'}))
    sender = forms.EmailField(widget=forms.TextInput(attrs={'size': '40', 'class': 'form-control'}))
    message = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control'}))
    copy = forms.BooleanField(required=False)


class FilterProductForm(forms.Form):
    def get_choices_from_field(field):
        distinct_qs = Product.objects.all().values_list(field).distinct()
        choices = [(i[0], i[0]) for i in list(distinct_qs)]  # [(2,), (4,)] > [(2,2), (4.4)]
        choices.sort()
        return choices

    os_select = forms.ChoiceField(choices=(
        ('io', 'iOS'),
        ('andr', 'Android')
    ), widget=forms.RadioSelect)
    ram_select = forms.ChoiceField(choices=get_choices_from_field('ram'),
                                   widget=forms.RadioSelect
                                   )
    diagonal_select = forms.ChoiceField(choices=get_choices_from_field('diagonal'),
                                        widget=forms.Select
                                        )
    processor_select = forms.ChoiceField(choices=get_choices_from_field('processor'))



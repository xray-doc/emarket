from django import forms
from orders.models import Order


class OrderForm(forms.ModelForm):

    class Meta:
        model = Order
        fields = [
            'customer_name',
            'customer_phone',
            'customer_email',
            'customer_address',
            'comments'
        ]

        widgets = {
            'customer_name': forms.TextInput(attrs=({'class': 'form-control'})),
            'customer_phone': forms.TextInput(attrs=({'class': 'form-control', 'type': 'tel'})),
            'customer_email': forms.TextInput(attrs=({'class': 'form-control'})),
            'customer_address': forms.TextInput(attrs=({'class': 'form-control'})),
            'comments': forms.Textarea(attrs=({'class': 'form-control'}))
        }

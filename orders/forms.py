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
            'customer_name': forms.TextInput(attrs=({'class': 'form-control',
                                                     'placeholder': 'Ivan Ivanov'})),
            'customer_phone': forms.TextInput(attrs=({'class': 'form-control',
                                                      'type': 'tel',
                                                      'placeholder': '+7 (777) 777 77 77'})),
            'customer_email': forms.TextInput(attrs=({'class': 'form-control',
                                                      'placeholder': 'emailaddress@site.ru'})),
            'customer_address': forms.TextInput(attrs=({'class': 'form-control',
                                                        'placeholder': 'Your real address'})),
            'comments': forms.Textarea(attrs=({'class': 'form-control'}))
        }
        labels = {
            'customer_name': 'Your full name',
            'customer_phone': 'Phone',
            'customer_email': 'Email',
            'customer_address': 'Address',
            'comments': 'Comments to order'
        }



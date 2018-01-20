from django import forms


class CheckoutContactForm(forms.Form):
    name = forms.CharField(required=True)
    phone = forms.CharField(required=True)
    email = forms.EmailField(required=False)
    address = forms.CharField(required=False)
    comments = forms.CharField(required=False)


from django.shortcuts import render
from rest_framework import generics
from rest_framework.response import Response
from django.db.models import Q
from products.models import Product
from .permissions import IsStaffOrReadOnly
from .serializers import ProductSerializer


class ProductAPIView(generics.ListAPIView):
    permission_classes = [IsStaffOrReadOnly]
    serializer_class = ProductSerializer

    def get_queryset(self):

        # In his request, client may specify fields (tablet characteristics) to show.
        # For example: name, price, proc etc. The request looks like: q=name*price*processor.
        query = self.request.GET.get("q")
        if query is not None:
            fields = query.split('*')
        else:
            fields = ['name']

        # Here we say serializer what fields to show.
        self.serializer_class.Meta.fields = fields

        qs = Product.objects.all()

        return qs


class ProductRudView(generics.RetrieveUpdateDestroyAPIView): # DetailView CreateView FormView
    serializer_class        = ProductSerializer
    permission_classes      = [IsStaffOrReadOnly]

    def get_queryset(self):
        return Product.objects.all()


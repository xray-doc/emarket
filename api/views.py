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
    fields_to_show = ['name']

    def post(self, request, *args, **kwargs):
        fields = self.request.data.get('q')
        if fields:
            self.fields_to_show = fields
        return super().get(self)

    def get_queryset(self):
        self.serializer_class.Meta.fields = self.fields_to_show
        qs = Product.objects.all()

        return qs


class ProductRudView(generics.RetrieveUpdateDestroyAPIView): # DetailView CreateView FormView
    serializer_class        = ProductSerializer
    permission_classes      = [IsStaffOrReadOnly]

    def get_queryset(self):
        return Product.objects.all()


from django.shortcuts import render
from rest_framework import generics
from rest_framework.response import Response
from django.db.models import Q
from products.models import Product
from .permissions import IsStaffOrReadOnly
from .serializers import ProductSerializer


class ProductAPIView(generics.ListAPIView):
    permission_classes = [IsStaffOrReadOnly]

    def get(self, request):
        products = Product.objects.all()

        # In his request, client may specify fields (tablet characteristics) to show.
        # For example: name, price, processor etc.
        query = request.GET.get("q")
        if query is not None:
            fields = query.split('*')
        else:
            fields = ['name']

        serialized_products = [ProductSerializer(p, fields=fields).data for p in products]

        return Response(serialized_products)


class ProductRudView(generics.RetrieveUpdateDestroyAPIView): # DetailView CreateView FormView
    serializer_class        = ProductSerializer
    permission_classes      = [IsStaffOrReadOnly]

    def get_queryset(self):
        return Product.objects.all()


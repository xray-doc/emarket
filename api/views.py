from django.shortcuts import render
from rest_framework import generics
from django.db.models import Q


from products.models import Product
from .permissions import IsStaffOrReadOnly
from .serializers import ProductSerializer



class ProductAPIView(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [IsStaffOrReadOnly]

    def get_queryset(self):
        qs = Product.objects.all()

        # Request may contain query with parameters that client interested in.
        # For instance: only name, ram and processor.
        # Params shoud be a string with * between them, like: name*ram*processor
        query = self.request.GET.get("q")
        if query is not None:
            queryset = query.split('*')

            qs = qs.filter(name__icontains=query)
        return qs


class ProductRudView(generics.RetrieveUpdateDestroyAPIView): # DetailView CreateView FormView
    serializer_class        = ProductSerializer
    permission_classes      = [IsStaffOrReadOnly]

    def get_queryset(self):
        return Product.objects.all()


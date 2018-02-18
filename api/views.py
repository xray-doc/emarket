from django.shortcuts import render
from rest_framework import generics

from products.models import Product
from .permissions import IsAdminOrReadOnly
from .serializers import ProductSerializer



class ProductAPIView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]


class ProductRudView(generics.RetrieveUpdateDestroyAPIView): # DetailView CreateView FormView
    serializer_class        = ProductSerializer
    permission_classes      = [IsAdminOrReadOnly]
    #queryset                = BlogPost.objects.all()

    def get_queryset(self):
        return Product.objects.all()

    # def get_serializer_context(self, *args, **kwargs):
    #     return {"request": self.request}

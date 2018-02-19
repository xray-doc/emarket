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
        query = self.request.GET.get("q")
        if query is not None:
            qs = qs.filter(name__icontains=query)
        return qs


class ProductRudView(generics.RetrieveUpdateDestroyAPIView): # DetailView CreateView FormView
    serializer_class        = ProductSerializer
    permission_classes      = [IsStaffOrReadOnly]
    #queryset                = BlogPost.objects.all()

    def get_queryset(self):
        return Product.objects.all()

    # def get_serializer_context(self, *args, **kwargs):
    #     return {"request": self.request}

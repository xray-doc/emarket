from django.conf.urls import url


from .views import ProductAPIView, ProductRudView

urlpatterns = [
    url(r'^products-list/$', ProductAPIView.as_view(), name='products-list'),
    url(r'^products-rud/(?P<pk>\d+)/$', ProductRudView.as_view(), name='product-rud')
]   
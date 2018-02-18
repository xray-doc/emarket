from django.conf.urls import url


from .views import ProductAPIView

urlpatterns = [
    url(r'^$', ProductAPIView.as_view(), name='product-list'),
    #url(r'^(?P<pk>\d+)/$', ProductRudView.as_view(), name='product-rud')
]   
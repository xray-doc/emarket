from django.conf.urls import url

from .views import *


urlpatterns = [
    url(r'^register/', register_view, name='register'),
    url(r'^login/', login_view, name='login'),
    url(r'^logout/', logout_view, name='logout'),
    url(r'^edit-profile/', edit_profile_view, name='edit-profile'),
    #url(r'^profile/', profile_view, name='profile')
    url(r'^profile/(?:(?P<username>\w+)/)?$', profile_view, name='profile')
]

#url(r'^(?P<product_id>\w+)/$', views.product, name='product'),
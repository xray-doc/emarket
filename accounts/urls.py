from django.conf.urls import url

from .views import *


urlpatterns = [
    url(r'^register/', RegisterView.as_view(), name='register'),
    url(r'^login/', LoginView.as_view(), name='login'),
    url(r'^logout/', LogoutView.as_view(), name='logout'),
    url(r'^edit-profile/', EditProfileView.as_view(), name='edit-profile'),
    #url(r'^profile/', profile_view, name='profile')
    url(r'^profile/(?:(?P<username>\w+)/)?$', ProfileView.as_view(), name='profile')
]

#url(r'^(?P<product_id>\w+)/$', views.product, name='product'),
from django.conf.urls import url

from .views import *



urlpatterns = [
    url(r'^register/', register_view, name='register'),
    url(r'^login/', login_view, name='login'),
    url(r'^logout/', logout_view, name='logout'),
    url(r'^edit-profile/', edit_profile_view, name='edit_profile')
]
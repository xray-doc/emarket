from django.contrib.auth import (
    authenticate,
    get_user_model,
    login,
    logout,
    )
from django.views.generic.edit import FormView, UpdateView
from django.views.generic.base import RedirectView, TemplateView
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.urlresolvers import reverse

from .forms import UserLoginForm, UserRegisterForm, EditProfileForm
from .models import Profile
from orders.models import Order

User = get_user_model()


class LoginView(FormView):

    template_name = 'accounts/form.html'
    form_class = UserLoginForm
    title = 'Login'

    def form_valid(self, form):
        user = authenticate(**form.cleaned_data)
        login(self.request, user)
        try:
            self.success_url = self.request.GET['next']
        except:
            self.success_url = '/'
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.title
        return context


class RegisterView(FormView):

    template_name = 'accounts/form.html'
    form_class = UserRegisterForm
    title = 'Register'

    def form_valid(self, form):
        user = form.save(commit=False)
        password = form.cleaned_data.get('password')
        user.set_password(password)
        user.save()
        new_user = authenticate(username=user.username, password=password)
        login(self.request, new_user)
        self.success_url = reverse("accounts:edit-profile")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.title
        return context


class LogoutView(RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        logout(self.request)
        return '/'


class EditProfileView(LoginRequiredMixin, UpdateView):

    model = Profile
    login_url = '/accounts/login/'
    template_name = 'accounts/form.html'
    form_class = EditProfileForm
    title = 'Edit profile'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.title
        return context

    def get_object(self, queryset=None):
        user = self.request.user
        obj, created = Profile.objects.get_or_create(user=user)
        return obj


class ProfileView(TemplateView):

    template_name = "accounts/profile.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.user == self.request.user: # self.user is requested user, not the authenticated one.
            # If you look at your own profile page
            # you can also see your orders,
            # but you can't see other's people orders on their pages
            context['orders'] = self.user.order_set.all() #Order.objects.filter(user=self.user)
        try:
            context['profile'] = self.user.profile_set.first() #Profile.objects.get(user=self.user)
        except:
            pass
        context['user'] = self.user
        return context

    def get(self, request, *args, **kwargs):
        if kwargs['username']:
            try:
                self.user = User.objects.get(username__iexact=kwargs['username'])
            except:
                pass
        else:
            self.user = self.request.user

        if not self.user.is_authenticated():
            return redirect(reverse('main'))
        return super().get(request, *args, **kwargs)

from django.contrib.auth import (
    get_user_model,
    login,
)
from django.test import TestCase
from django.urls import reverse
from mixer.backend.django import mixer

from ..forms import UserLoginForm, UserRegisterForm
from ..views import login_view

User = get_user_model()


class login_viewTestCase(TestCase):

    def setUp(self):
        test_user = User.objects.create_user(username='testuser', password='somepass')

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/accounts/login/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('accounts:login'))
        self.assertEqual(response.status_code, 200)

    def test_view_context(self):
        response = self.client.get(reverse('accounts:login'))
        self.assertEqual(response.context['title'], 'Login')
        self.assertEqual(response.context['form'].__class__, UserLoginForm)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('accounts:login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/form.html')

    def test_registered_user(self):
        user_obj = User.objects.get(username='testuser')
        response = self.client.get(reverse('main'))
        self.assertFalse(response.context['user'].is_authenticated())

        data = {'username': 'testuser', 'password': 'somepass'}
        response = self.client.post(reverse('accounts:login'), data)
        self.assertRedirects(response, '/', status_code=302, target_status_code=302)
        response = self.client.get(reverse('main'))
        self.assertTrue(response.context['user'].is_authenticated())

    def test_not_registered_user(self):
        data = {'username': 'testusernotregistered', 'password': 'somepass'}
        response = self.client.post(reverse('accounts:login'), data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/form.html')

    def test_form_is_not_valid(self):
        data = {'username': 'testuser', 'password': ''}
        response = self.client.post(reverse('accounts:login'), data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/form.html')


class register_viewTestCase(TestCase):

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/accounts/register/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('accounts:register'))
        self.assertEqual(response.status_code, 200)

    def test_view_context(self):
        response = self.client.get(reverse('accounts:register'))
        self.assertEqual(response.context['title'], 'Register')
        self.assertEqual(response.context['form'].__class__, UserRegisterForm)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('accounts:register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/form.html')

    def test_registering_with_valid_data(self):
        self.assertEqual(User.objects.count(), 0)

        data = {
            'username': 'testuser',
            'password': 'somepass',
            'email': 'test@test.com'
        }
        response = self.client.post(reverse('accounts:register'), data)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.first().username, 'testuser')
        self.assertTemplateNotUsed(response, 'accounts/form.html')
        self.assertRedirects(response, reverse("accounts:edit-profile"))

    def test_registering_with_invalid_data(self):
        self.assertEqual(User.objects.count(), 0)

        data = {'username': 'testuser'}
        response = self.client.post(reverse('accounts:register'), data)
        self.assertEqual(User.objects.count(), 0)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/form.html')


class logout_viewTestCase(TestCase):

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/accounts/logout/')
        self.assertEqual(response.status_code, 302)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('accounts:logout'))
        self.assertEqual(response.status_code, 302)

    def test_user_log_out(self):
        test_user = User.objects.create_user(username='testuser', password='somepass')
        self.client.login(username='testuser', password='somepass')
        response = self.client.get(reverse('main'))
        self.assertTrue(response.context['user'].is_authenticated())

        response = self.client.get(reverse('accounts:logout'))
        response = self.client.get(reverse('main'))
        self.assertFalse(response.context['user'].is_authenticated())

    def test_redirect(self):
        response = self.client.get(reverse('accounts:logout'))
        self.assertRedirects(response, '/', status_code=302, target_status_code=302)


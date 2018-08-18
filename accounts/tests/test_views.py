from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from mixer.backend.django import mixer

from ..views import login_view

User = get_user_model()


class login_viewTestCase(TestCase):

    def setUp(self):
        test_user1 = User.objects.create_user(username='testuser', password='somepass')

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/accounts/login/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('accounts:login'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('accounts:login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/form.html')

    def test_registered_user(self):
        user_obj = User.objects.get(username='testuser')
        self.assertFalse(User.objects.get(username='testuser').last_login)

        data = {'username': 'testuser', 'password': 'somepass'}
        response = self.client.post(reverse('accounts:login'), data)
        self.assertRedirects(response, '/', status_code=302, target_status_code=302)
        self.assertTrue(User.objects.get(username='testuser').last_login)

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
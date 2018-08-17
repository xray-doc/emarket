from django.contrib.auth import get_user_model
from django.test import TestCase
from mixer.backend.django import mixer

from ..models import Profile
from ..forms import UserLoginForm, UserRegisterForm

User = get_user_model()


class UserLoginFormTestCase(TestCase):

    def setUp(self):
        user = User(username='testuser', email='test@test.com')
        user.set_password("somepass")
        user.save()

    def test_unregistered_user(self):
        data = {'username': "Harry", 'password': 'boxer11231'}
        form = UserLoginForm(data=data)
        self.assertFalse(form.is_valid())

    def test_registered_user(self):
        data = {'username': "testuser", 'password': 'somepass'}
        form = UserLoginForm(data=data)
        self.assertTrue(form.is_valid())

    def test_unactive_user(self):
        user = User.objects.first()
        user.is_active = False
        user.save()

        data = {'username': "testuser", 'password': 'somepass'}
        form = UserLoginForm(data=data)
        self.assertFalse(form.is_valid())


class UserRegisterFormTestCase(TestCase):

    def setUp(self):
        user = User(username='testuser', email='test@test.com')
        user.set_password("somepass")
        user.save()

    def test_clean_email_with_new_email(self):
        data = {
            'username': 'Harry',
            'password': 'somepass',
            'email': 'new_email@test.com'
        }
        form = UserRegisterForm(data=data)
        self.assertTrue(form.is_valid())

    def test_clean_email_with_existed_email(self):
        data = {
            'username': 'Harry',
            'password': 'somepass',
            'email': 'test@test.com'
        }
        form = UserRegisterForm(data=data)
        self.assertFalse(form.is_valid())


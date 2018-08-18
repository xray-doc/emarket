from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from mixer.backend.django import mixer

from ..views import login_view

User = get_user_model()


class login_viewTestCase(TestCase):

    def setUp(self):
        test_user1 = User.objects.create_user(username='testuser', password='somepass')

    def test_logging_in(self):
        response = self.client.get(reverse('accounts:register'))
        self.assertEqual(response.status_code, 200)

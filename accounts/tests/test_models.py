from django.test import TestCase
from mixer.backend.django import mixer

from ..models import Profile


class ProfileTestCase(TestCase):

    def setUp(self):
        profile = mixer.blend(Profile, first_name='Anna', second_name='Gutova')


    def test_get_full_name(self):
        profile = Profile.objects.first()
        full_name = profile.get_full_name()
        self.assertEqual(full_name, 'Anna Gutova')

    def test_str_method(self):
        profile = Profile.objects.first()
        profile.user.username = 'Ann'
        str_profile = str(profile)
        self.assertEqual(str_profile, 'Ann profile')



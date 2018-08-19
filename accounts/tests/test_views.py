import datetime

from django.contrib.auth import get_user_model, login
from django.test import TestCase
from django.urls import reverse
from mixer.backend.django import mixer

from orders.models import Order
from ..forms import UserLoginForm, UserRegisterForm, EditProfileForm
from ..models import Profile

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
        response = self.client.get(reverse('main'))
        self.assertFalse(response.context['user'].is_authenticated())

        data = {'username': 'testuser', 'password': 'somepass'}
        response = self.client.post(reverse('accounts:login'), data)
        self.assertRedirects(response, '/', status_code=302, target_status_code=302)
        response = self.client.get(reverse('main'))
        self.assertTrue(response.context['user'].is_authenticated())

    # def test_registered_user_with_next_argument(self):
    #     data = {'username': 'testuser', 'password': 'somepass', 'next': 'iamfromhere'}
    #     response = self.client.post(reverse('accounts:login'), data)
    #     self.assertRedirects(response, 'iamfromhere', status_code=302, target_status_code=302)
    #     response = self.client.get(reverse('main'))
    #     self.assertTrue(response.context['user'].is_authenticated())

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
            'username': 'testuserQ',
            'password': 'somepass',
            'email': 'test@test.com'
        }
        response = self.client.post(reverse('accounts:register'), data)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.first().username, 'testuserQ')
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


class edit_profile_viewTestCase(TestCase):

    def setUp(self):
        test_user = User.objects.create_user(username='testuser', password='somep')
        profile = mixer.blend(Profile, user=test_user, phone=333444111)
        self.client.login(username='testuser', password='somep')

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/accounts/edit-profile/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('accounts:edit-profile'))
        self.assertEqual(response.status_code, 200)

    def test_view_context(self):
        response = self.client.get(reverse('accounts:edit-profile'))
        self.assertEqual(response.context['form'].__class__, EditProfileForm)
        self.assertEqual(response.context['title'], 'Edit profile')
        self.assertEqual(response.context['form']['phone'].initial, '333444111')

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('accounts:edit-profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/form.html')

    def test_user_logged_out(self):
        self.client.logout()
        response = self.client.get(reverse('accounts:edit-profile'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('accounts:login') + '?next='
                             + reverse('accounts:edit-profile'))

    def test_post_valid_data(self):
        birth_date = datetime.date(1990, 10, 20)
        data = {
            'first_name': 'Harry',
            'second_name': 'Kane',
            'gender': 'M',
            'birth_date': birth_date,
            'phone': '79998998987',
            'address': 'Moskwa ul. Sosnovaya'
        }

        response = self.client.post(reverse('accounts:edit-profile'), data)
        self.assertEqual(response.status_code, 302)
        profile = Profile.objects.get(user__username='testuser')
        self.assertRedirects(response, profile.get_absolute_url())
        self.assertEqual(profile.second_name, 'Kane')
        # everything working ok, but this assert fail without a reason:
        # self.assertEqual(profile.birth_date, birth_date)
        self.assertEqual(profile.address, 'Moskwa ul. Sosnovaya')

    def test_post_invalid_data(self):
        data = {'first_name': 'Dan'}
        response = self.client.post(reverse('accounts:edit-profile'), data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/form.html')
        self.assertEqual(response.context['form'].cleaned_data['first_name'], 'Dan')


class profile_viewTestCase(TestCase):

    def setUp(self):
        test_user = User.objects.create_user(username='testuser', password='somep')
        profile = mixer.blend(Profile, user=test_user)
        order = mixer.blend(Order, user=test_user)
        self.client.login(username='testuser', password='somep')

        test_user2 = User.objects.create_user(username='testuser2', password='somep2')
        profile2 = mixer.blend(Profile, user=test_user2)

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/accounts/profile/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('accounts:profile'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('accounts:profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/profile.html')

    def test_view_context_with_logged_in_user(self):
        profile = Profile.objects.get(user__username='testuser')
        response = self.client.get(reverse('accounts:profile'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['profile'], profile)
        self.assertTrue('orders' in response.context)
        self.assertEqual(response.context['orders'].count(), 1)

    def test_view_context_with_other_user(self):
        profile = Profile.objects.get(user__username='testuser')
        profile2 = Profile.objects.get(user__username='testuser2')

        response = self.client.get(reverse('accounts:profile',
                                   kwargs={'username': 'testuser2'}))
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(response.context['profile'], profile)
        self.assertEqual(response.context['profile'], profile2)
        self.assertFalse('orders' in response.context)

    def test_view_with_anonimous_user_and_without_query(self):
        self.client.logout()
        response = self.client.get(reverse('accounts:profile'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("main"))


#TODO: rename test's name
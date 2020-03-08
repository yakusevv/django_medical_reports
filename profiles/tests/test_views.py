import datetime

from django.utils import timezone
from django.test import TestCase
from django.urls import reverse

from profiles.models import Profile, ProfileReportAutofillTemplate
from reports.models import (
                            Report,
                            Country,
                            Region,
                            District,
                            City,
                        )

from django.contrib.auth.models import User

class AccessRequiredViewTest(TestCase):

    @classmethod
    def setUpTestData(self):

        test_country1 = Country.objects.create(name='testcountry1')
        test_country1.save()
        test_region1 = Region.objects.create(name='testregion1', country=test_country1)
        test_region1.save()
        test_district1 = District.objects.create(name='testdistrict1', region=test_region1)
        test_district1.save()
        test_city1 = City.objects.create(name='testcity1', district=test_district1)
        test_city1.save()

        test_country2 = Country.objects.create(name='testcountry2')
        test_country1.save()
        test_region2 = Region.objects.create(name='testregion2', country=test_country2)
        test_region2.save()
        test_district2 = District.objects.create(name='testdistrict2', region=test_region2)
        test_district2.save()
        test_city2 = City.objects.create(name='testcity21', district=test_district2)
        test_city2.save()

        test_user11 = User.objects.create_user(username='testuser11', password='12345', is_staff=False)
        test_profile11 = Profile.objects.create(user=test_user11, num_col='123', city=test_city1)
        test_user11.save()
        test_profile11.save()

        test_user12 = User.objects.create_user(username='testuser12', password='12345', is_staff=True)
        test_user12.save()
        test_profile12 = Profile.objects.create(user=test_user12, num_col='321', city=test_city1)
        test_profile12.save()

        test_user21 = User.objects.create_user(username='testuser21', password='12345', is_staff=False)
        test_profile21 = Profile.objects.create(user=test_user21, num_col='1230', city=test_city2)
        test_user21.save()
        test_profile21.save()

        test_template11 = ProfileReportAutofillTemplate.objects.create(doctor=test_profile11)
        test_template11.save()

        test_template12 = ProfileReportAutofillTemplate.objects.create(doctor=test_profile12)
        test_template12.save()

        test_template21 = ProfileReportAutofillTemplate.objects.create(doctor=test_profile21)
        test_template21.save()

#profile detail view
    def test_redirect_if_not_logged_in_profile_detail(self):
        profilepk = Profile.objects.all()[0].pk
        resp = self.client.get(reverse('profile_detail_url', kwargs={'pk': profilepk}))
        self.assertRedirects(resp, '/accounts/login/?next=/profiles/{}/detail/'.format(profilepk))

    def test_forbidden_if_not_users_profile_profile_detail(self):
        profilepk = Profile.objects.get(user__username='testuser12').pk
        login = self.client.login(username='testuser11', password='12345')
        resp = self.client.get(reverse('profile_detail_url', kwargs={'pk': profilepk}))

        self.assertEqual(resp.status_code, 403)

    def test_success_if_users_profile_profile_detail(self):
        profilepk = Profile.objects.get(user__username='testuser11').pk
        login = self.client.login(username='testuser11', password='12345')
        resp = self.client.get(reverse('profile_detail_url', kwargs={'pk': profilepk}))

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'profiles/profile_detail.html')

    def test_success_if_user_is_staff_and_not_users_profile_profile_detail(self):
        profilepk = Profile.objects.get(user__username='testuser11').pk
        login = self.client.login(username='testuser12', password='12345')
        resp = self.client.get(reverse('profile_detail_url', kwargs={'pk': profilepk}))

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'profiles/profile_detail.html')

    def test_forbidden_if_not_country_case_profile_detail(self):
        profilepk = Profile.objects.get(user__username='testuser21').pk
        login = self.client.login(username='testuser12', password='12345')
        resp = self.client.get(reverse('profile_detail_url', kwargs={'pk': profilepk}))

        self.assertEqual(resp.status_code, 403)

#ProfileReportAutofillTemplate update
    def test_redirect_if_not_logged_in_template_update(self):
        templatepk = ProfileReportAutofillTemplate.objects.all()[0].pk
        resp = self.client.get(reverse('profile_template_update_url', kwargs={'pk': templatepk}))
        self.assertRedirects(resp, '/accounts/login/?next=/profiles/templates/{}/update_template/'.format(templatepk))

    def test_forbidden_if_not_users_template_template_update(self):
        doctor = User.objects.get(username='testuser12').profile
        templatepk = ProfileReportAutofillTemplate.objects.filter(doctor=doctor)[0].pk
        login = self.client.login(username='testuser11', password='12345')
        resp = self.client.get(reverse('profile_template_update_url', kwargs={'pk': templatepk}))

        self.assertEqual(resp.status_code, 403)

    def test_success_if_users_template_template_update(self):
        doctor = User.objects.get(username='testuser11').profile
        templatepk = ProfileReportAutofillTemplate.objects.filter(doctor=doctor)[0].pk
        login = self.client.login(username='testuser11', password='12345')
        resp = self.client.get(reverse('profile_template_update_url', kwargs={'pk': templatepk}))

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'profiles/profile_template_update.html')

    def test_success_if_user_is_staff_and_not_users_template_template_update(self):
        doctor = User.objects.get(username='testuser11').profile
        templatepk = ProfileReportAutofillTemplate.objects.filter(doctor=doctor)[0].pk
        login = self.client.login(username='testuser12', password='12345')
        resp = self.client.get(reverse('profile_template_update_url', kwargs={'pk': templatepk}))

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'profiles/profile_template_update.html')

    def test_forbidden_if_not_country_case_template_update(self):
        doctor = User.objects.get(username='testuser21').profile
        templatepk = ProfileReportAutofillTemplate.objects.filter(doctor=doctor)[0].pk
        login = self.client.login(username='testuser12', password='12345')
        resp = self.client.get(reverse('profile_template_update_url', kwargs={'pk': templatepk}))

        self.assertEqual(resp.status_code, 403)

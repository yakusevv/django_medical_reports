from django.test import TestCase
from django.urls import reverse

from profiles.models import Profile
from reports.models import Report, Country, Region, District, City

from django.contrib.auth.models import User

class LoginRequiredViewTest(TestCase):

    def setUp(self):

        test_country = Country.objects.create(name='testcountry')
        test_country.save()
        test_region = Region.objects.create(name='testregion', country=test_country)
        test_region.save()
        test_district = District.objects.create(name='testdistrict', region=test_region)
        test_district.save()
        test_city1 = City.objects.create(name='testcity1', district=test_district)
        test_city1.save()
        test_city2 = City.objects.create(name='testcity2', district=test_district)
        test_city2.save()

        test_user1 = User.objects.create_user(username='testuser1', password='12345', is_staff=False)
        test_profile1 = Profile.objects.create(user=test_user1, num_col='123', city=test_city1)
        test_user1.save()
        test_profile1.save()

        test_user2 = User.objects.create_user(username='testuser2', password='12345', is_staff=True)
        test_user2.save()
        test_profile2 = Profile.objects.create(user=test_user2, num_col='321', city=test_city2)
        test_profile2.save()


    def test_redirect_if_not_logged_in_list(self):
        resp = self.client.get(reverse('reports_list_url'))
        self.assertRedirects(resp, '/accounts/login/?next=/reports/')


    def test_logged_in_uses_correct_template_list(self):
        login = self.client.login(username='testuser1', password='12345')
        resp = self.client.get(reverse('reports_list_url'))

        self.assertEqual(str(resp.context['user']), 'testuser1')

        self.assertEqual(resp.status_code, 200)

        self.assertTemplateUsed(resp, 'reports/reports_list.html')


    def test_redirect_if_not_logged_in_create(self):
        resp = self.client.get(reverse('report_create_url'))
        self.assertRedirects(resp, '/accounts/login/?next=/reports/create/')


    def test_logged_in_uses_correct_template_list(self):
        login = self.client.login(username='testuser1', password='12345')
        resp = self.client.get(reverse('report_create_url'))

        self.assertEqual(str(resp.context['user']), 'testuser1')

        self.assertEqual(resp.status_code, 200)

        self.assertTemplateUsed(resp, 'reports/report_create.html')

    def test_redirect_if_not_logged_in_price_table(self):
        countrypk = Country.objects.all()[0].pk
        resp = self.client.get(reverse('price_table_url', kwargs={'pk': countrypk,}))
        self.assertRedirects(resp, '/accounts/login/?next=/reports/price_table/{}/'.format(countrypk))

    def test_forbidden_if_not_staff_price_table(self):
        countrypk = Country.objects.all()[0].pk
        login = self.client.login(username='testuser1', password='12345')
        resp = self.client.get(reverse('price_table_url', kwargs={'pk': countrypk,}))

        self.assertEqual(resp.status_code, 403)

    def test_logged_in_uses_correct_template_price_table(self):
        countrypk = Country.objects.all()[0].pk
        login = self.client.login(username='testuser2', password='12345')
        resp = self.client.get(reverse('price_table_url', kwargs={'pk': countrypk,}))
        self.assertEqual(str(resp.context['user']), 'testuser2')

        self.assertEqual(resp.status_code, 200)

        self.assertTemplateUsed(resp, 'reports/price_table_view.html')

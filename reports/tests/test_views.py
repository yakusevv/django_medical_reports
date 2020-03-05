import datetime

from django.utils import timezone
from django.test import TestCase
from django.urls import reverse

from profiles.models import Profile
from reports.models import (
                            Report,
                            Country,
                            Region,
                            District,
                            City,
                            TypeOfVisit,
                            Company,
                            Disease,
                            PriceGroup,
                        )

from django.contrib.auth.models import User

class AccessRequiredViewTest(TestCase):

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

        test_price_group = PriceGroup.objects.create(name='pricegroup1')
        test_price_group.save()

        test_company = Company.objects.create(name='testcompany', price_group=test_price_group)
        test_company.save()

        test_type_of_visit = TypeOfVisit.objects.create(name='1', country=test_country)
        test_type_of_visit.save()

        test_disease = Disease.objects.create(name='testdisease', country=test_country)
        test_disease.save()

        test_report1 = Report.objects.create(
                    ref_number = 'A123',
                    company_ref_number = '12345',
                    company = test_company,
                    patients_first_name = 'Fname1',
                    patients_last_name = 'Lname1',
                    patients_date_of_birth = timezone.now() - datetime.timedelta(days=9999),
                    patients_policy_number = '123456789',
                    type_of_visit = test_type_of_visit,
                    visit_price = '321',
                    visit_price_doctor = '123',
                    date_of_visit = timezone.now() - datetime.timedelta(days=2),
                    city = test_city1,
                    cause_of_visit = 'testcause',
                    checkup = 'testcheckup',
                    additional_checkup = 'testadditionalcheckup',
#                    diagnosis = test_disease,
                    prescription = 'testprescription',
                    doctor = test_profile1
        )
        test_report1.diagnosis.add(test_disease)
        test_report1.save()

        test_report2 = Report.objects.create(
                    ref_number = 'B123',
                    company_ref_number = '12345',
                    company = test_company,
                    patients_first_name = 'Fname2',
                    patients_last_name = 'Lname2',
                    patients_date_of_birth = timezone.now() - datetime.timedelta(days=9999),
                    patients_policy_number = '123456789',
                    type_of_visit = test_type_of_visit,
                    visit_price = '321',
                    visit_price_doctor = '123',
                    date_of_visit = timezone.now() - datetime.timedelta(days=2),
                    city = test_city1,
                    cause_of_visit = 'testcause',
                    checkup = 'testcheckup',
                    additional_checkup = 'testadditionalcheckup',
                    prescription = 'testprescription',
                    doctor = test_profile2
        )
        test_report1.diagnosis.add(test_disease)
        test_report2.save()

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

    def test_redirect_if_not_logged_in_report_detail(self):
        reportpk = Report.objects.all()[0].pk
        resp = self.client.get(reverse('report_detail_url', kwargs={'pk': reportpk}))
        self.assertRedirects(resp, '/accounts/login/?next=/reports/{}/view/'.format(reportpk))

    def test_forbidden_if_not_users_report_report_detail(self):
        reportpk = Report.objects.get(ref_number='B123').pk
        login = self.client.login(username='testuser1', password='12345')
        resp = self.client.get(reverse('report_detail_url', kwargs={'pk': reportpk}))

        self.assertEqual(resp.status_code, 403)

    def test_success_if_users_report_report_detail(self):
        reportpk = Report.objects.get(ref_number='A123').pk
        login = self.client.login(username='testuser1', password='12345')
        resp = self.client.get(reverse('report_detail_url', kwargs={'pk': reportpk}))

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'reports/report_detail.html')

    def test_success_if_user_is_staff_and_not_users_report_report_detail(self):
        reportpk = Report.objects.get(ref_number='A123').pk
        login = self.client.login(username='testuser2', password='12345')
        resp = self.client.get(reverse('report_detail_url', kwargs={'pk': reportpk}))

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'reports/report_detail.html')

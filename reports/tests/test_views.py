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

        test_price_group = PriceGroup.objects.create(name='pricegroup1')
        test_price_group.save()

        test_company = Company.objects.create(name='testcompany', price_group=test_price_group)
        test_company.save()

        test_type_of_visit1 = TypeOfVisit.objects.create(name='1', country=test_country1)
        test_type_of_visit1.save()

        test_type_of_visit2 = TypeOfVisit.objects.create(name='2', country=test_country2)
        test_type_of_visit2.save()

        test_disease1 = Disease.objects.create(name='testdisease1', country=test_country1)
        test_disease1.save()

        test_disease2 = Disease.objects.create(name='testdisease2', country=test_country2)
        test_disease2.save()

        test_report11 = Report.objects.create(
                    ref_number = 'A123',
                    company_ref_number = '12345',
                    company = test_company,
                    patients_first_name = 'Fname1',
                    patients_last_name = 'Lname1',
                    patients_date_of_birth = timezone.now() - datetime.timedelta(days=9999),
                    patients_policy_number = '123456789',
                    type_of_visit = test_type_of_visit1,
                    visit_price = '321',
                    visit_price_doctor = '123',
                    date_of_visit = timezone.now() - datetime.timedelta(days=2),
                    city = test_city1,
                    cause_of_visit = 'testcause',
                    checkup = 'testcheckup',
                    additional_checkup = 'testadditionalcheckup',
                    prescription = 'testprescription',
                    doctor = test_profile11
        )
        test_report11.diagnosis.add(test_disease1)
        test_report11.save()

        test_report12 = Report.objects.create(
                    ref_number = 'B123',
                    company_ref_number = '12345',
                    company = test_company,
                    patients_first_name = 'Fname2',
                    patients_last_name = 'Lname2',
                    patients_date_of_birth = timezone.now() - datetime.timedelta(days=9999),
                    patients_policy_number = '123456789',
                    type_of_visit = test_type_of_visit1,
                    visit_price = '321',
                    visit_price_doctor = '123',
                    date_of_visit = timezone.now() - datetime.timedelta(days=2),
                    city = test_city1,
                    cause_of_visit = 'testcause',
                    checkup = 'testcheckup',
                    additional_checkup = 'testadditionalcheckup',
                    prescription = 'testprescription',
                    doctor = test_profile12
        )
        test_report12.diagnosis.add(test_disease1)
        test_report12.save()

        test_report21 = Report.objects.create(
                    ref_number = 'C123',
                    company_ref_number = '12345',
                    company = test_company,
                    patients_first_name = 'Fname1',
                    patients_last_name = 'Lname1',
                    patients_date_of_birth = timezone.now() - datetime.timedelta(days=9999),
                    patients_policy_number = '123456789',
                    type_of_visit = test_type_of_visit2,
                    visit_price = '321',
                    visit_price_doctor = '123',
                    date_of_visit = timezone.now() - datetime.timedelta(days=2),
                    city = test_city2,
                    cause_of_visit = 'testcause',
                    checkup = 'testcheckup',
                    additional_checkup = 'testadditionalcheckup',
                    prescription = 'testprescription',
                    doctor = test_profile21
        )
        test_report21.diagnosis.add(test_disease2)
        test_report21.save()

        test_report22 = Report.objects.create(
                    ref_number = 'D123',
                    company_ref_number = '12345',
                    company = test_company,
                    patients_first_name = 'Fname2',
                    patients_last_name = 'Lname2',
                    patients_date_of_birth = timezone.now() - datetime.timedelta(days=9999),
                    patients_policy_number = '123456789',
                    type_of_visit = test_type_of_visit2,
                    visit_price = '321',
                    visit_price_doctor = '123',
                    date_of_visit = timezone.now() - datetime.timedelta(days=2),
                    city = test_city2,
                    cause_of_visit = 'testcause',
                    checkup = 'testcheckup',
                    additional_checkup = 'testadditionalcheckup',
                    prescription = 'testprescription',
                    doctor = test_profile11
        )
        test_report22.diagnosis.add(test_disease2)
        test_report22.save()

#reports list view
    def test_redirect_if_not_logged_in_reports_list(self):
        resp = self.client.get(reverse('reports_list_url'))
        self.assertRedirects(resp, '/accounts/login/?next=/reports/')

    def test_logged_in_uses_correct_template_reports_list(self):
        login = self.client.login(username='testuser11', password='12345')
        resp = self.client.get(reverse('reports_list_url'))

        self.assertEqual(str(resp.context['user']), 'testuser11')

        for report in resp.context['report_list']:
            self.assertEqual(resp.context['user'].profile, report.doctor)
            self.assertEqual(resp.context['user'].profile.city.district.region.country, report.city.district.region.country)

        self.assertEqual(resp.status_code, 200)

        self.assertTemplateUsed(resp, 'reports/reports_list.html')

    def test_user_is_staff_correct_template_reports_list(self):
        login = self.client.login(username='testuser12', password='12345')
        resp = self.client.get(reverse('reports_list_url'))

        self.assertEqual(str(resp.context['user']), 'testuser12')

        report_list = resp.context['report_list']
        doctors_country = resp.context['user'].profile.city.district.region.country

        self.assertEqual(set(report_list), set(Report.objects.filter(
                                        city__district__region__country=doctors_country
                                        )
                        ))
        self.assertEqual(resp.status_code, 200)

        self.assertTrue(resp.context['user'].is_staff)

        self.assertTemplateUsed(resp, 'reports/reports_list.html')

#report create view
    def test_redirect_if_not_logged_in_create_report(self):
        resp = self.client.get(reverse('report_create_url'))
        self.assertRedirects(resp, '/accounts/login/?next=/reports/create/')

    def test_logged_in_uses_correct_template_report_create(self):
        login = self.client.login(username='testuser11', password='12345')
        resp = self.client.get(reverse('report_create_url'))

        self.assertEqual(str(resp.context['user']), 'testuser11')

        self.assertEqual(resp.status_code, 200)

        self.assertTemplateUsed(resp, 'reports/report_create.html')

#price table view
    def test_redirect_if_not_logged_in_price_table(self):
        countrypk = Country.objects.get(name='testcountry1').pk
        resp = self.client.get(reverse('price_table_url', kwargs={'pk': countrypk,}))
        self.assertRedirects(resp, '/accounts/login/?next=/reports/price_table/{}/'.format(countrypk))

    def test_forbidden_if_not_staff_price_table(self):
        countrypk = Country.objects.get(name='testcountry1').pk
        login = self.client.login(username='testuser11', password='12345')
        resp = self.client.get(reverse('price_table_url', kwargs={'pk': countrypk,}))

        self.assertEqual(resp.status_code, 403)

    def test_logged_in_uses_correct_template_price_table(self):
        countrypk = Country.objects.get(name='testcountry1').pk
        login = self.client.login(username='testuser12', password='12345')
        resp = self.client.get(reverse('price_table_url', kwargs={'pk': countrypk,}))
        self.assertEqual(str(resp.context['user']), 'testuser12')

        self.assertEqual(resp.status_code, 200)

        self.assertTemplateUsed(resp, 'reports/price_table_view.html')

#report detail view
    def test_redirect_if_not_logged_in_report_detail(self):
        reportpk = Report.objects.all()[0].pk
        resp = self.client.get(reverse('report_detail_url', kwargs={'pk': reportpk}))
        self.assertRedirects(resp, '/accounts/login/?next=/reports/{}/view/'.format(reportpk))

    def test_forbidden_if_not_users_report_report_detail(self):
        reportpk = Report.objects.get(ref_number='B123', doctor__user__username='testuser12').pk
        login = self.client.login(username='testuser11', password='12345')
        resp = self.client.get(reverse('report_detail_url', kwargs={'pk': reportpk}))

        self.assertEqual(resp.status_code, 403)

    def test_success_if_users_report_report_detail(self):
        reportpk = Report.objects.get(ref_number='A123', doctor__user__username='testuser11').pk
        login = self.client.login(username='testuser11', password='12345')
        resp = self.client.get(reverse('report_detail_url', kwargs={'pk': reportpk}))

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'reports/report_detail.html')

        reportpk = Report.objects.get(ref_number='D123', doctor__user__username='testuser11').pk

        resp = self.client.get(reverse('report_detail_url', kwargs={'pk': reportpk}))

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'reports/report_detail.html')

    def test_success_if_user_is_staff_and_not_users_report_report_detail(self):
        reportpk = Report.objects.get(ref_number='A123', doctor__user__username='testuser11').pk
        login = self.client.login(username='testuser12', password='12345')
        resp = self.client.get(reverse('report_detail_url', kwargs={'pk': reportpk}))

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'reports/report_detail.html')

#    def test_forbidden_if_not_country_case_report_detail(self):
#        reportpk = Report.objects.get(ref_number='C123', doctor__user__username='testuser21').pk
#        login = self.client.login(username='testuser12', password='12345')
#        resp = self.client.get(reverse('report_detail_url', kwargs={'pk': reportpk}))

#        self.assertEqual(resp.status_code, 403)

#report update view
    def test_redirect_if_not_logged_in_report_update(self):
        reportpk = Report.objects.all()[0].pk
        resp = self.client.get(reverse('report_update_url', kwargs={'pk': reportpk}))
        self.assertRedirects(resp, '/accounts/login/?next=/reports/{}/update/'.format(reportpk))

    def test_forbidden_if_not_users_report_report_update(self):
        reportpk = Report.objects.get(ref_number='B123', doctor__user__username='testuser12').pk
        login = self.client.login(username='testuser11', password='12345')
        resp = self.client.get(reverse('report_update_url', kwargs={'pk': reportpk}))

        self.assertEqual(resp.status_code, 403)

    def test_success_if_users_report_report_update(self):
        reportpk = Report.objects.get(ref_number='A123', doctor__user__username='testuser11').pk
        login = self.client.login(username='testuser11', password='12345')
        resp = self.client.get(reverse('report_update_url', kwargs={'pk': reportpk}))

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'reports/report_update.html')

    def test_success_if_user_is_staff_and_not_users_report_report_update(self):
        reportpk = Report.objects.get(ref_number='A123', doctor__user__username='testuser11').pk
        login = self.client.login(username='testuser12', password='12345')
        resp = self.client.get(reverse('report_update_url', kwargs={'pk': reportpk}))

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'reports/report_update.html')

    def test_forbidden_if_not_country_case_report_update(self):
        reportpk = Report.objects.get(ref_number='D123', doctor__user__username='testuser11').pk
        login = self.client.login(username='testuser11', password='12345')
        resp = self.client.get(reverse('report_update_url', kwargs={'pk': reportpk}))

        self.assertEqual(resp.status_code, 403)

        login = self.client.login(username='testuser12', password='12345')
        resp = self.client.get(reverse('report_delete_url', kwargs={'pk': reportpk}))

        self.assertEqual(resp.status_code, 403)

#report images update
    def test_redirect_if_not_logged_in_report_images_update(self):
        reportpk = Report.objects.all()[0].pk
        resp = self.client.get(reverse('report_images_update_url', kwargs={'pk': reportpk}))
        self.assertRedirects(resp, '/accounts/login/?next=/reports/{}/update/images/'.format(reportpk))

    def test_forbidden_if_not_users_report_report_images_update(self):
        reportpk = Report.objects.get(ref_number='B123', doctor__user__username='testuser12').pk
        login = self.client.login(username='testuser11', password='12345')
        resp = self.client.get(reverse('report_images_update_url', kwargs={'pk': reportpk}))

        self.assertEqual(resp.status_code, 403)

    def test_success_if_users_report_report_images_update(self):
        reportpk = Report.objects.get(ref_number='A123', doctor__user__username='testuser11').pk
        login = self.client.login(username='testuser11', password='12345')
        resp = self.client.get(reverse('report_images_update_url', kwargs={'pk': reportpk}))

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'reports/report_images_update.html')

    def test_success_if_user_is_staff_and_not_users_report_report_images_update(self):
        reportpk = Report.objects.get(ref_number='A123', doctor__user__username='testuser11').pk
        login = self.client.login(username='testuser12', password='12345')
        resp = self.client.get(reverse('report_images_update_url', kwargs={'pk': reportpk}))

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'reports/report_images_update.html')

    def test_forbidden_if_not_country_case_report_images_update(self):
        reportpk = Report.objects.get(ref_number='D123', doctor__user__username='testuser11').pk
        login = self.client.login(username='testuser11', password='12345')
        resp = self.client.get(reverse('report_images_update_url', kwargs={'pk': reportpk}))

        self.assertEqual(resp.status_code, 403)

        login = self.client.login(username='testuser12', password='12345')
        resp = self.client.get(reverse('report_delete_url', kwargs={'pk': reportpk}))

        self.assertEqual(resp.status_code, 403)

#delete report view
    def test_redirect_if_not_logged_in_report_delete(self):
        reportpk = Report.objects.all()[0].pk
        resp = self.client.get(reverse('report_delete_url', kwargs={'pk': reportpk}))
        self.assertRedirects(resp, '/accounts/login/?next=/reports/{}/delete/'.format(reportpk))

    def test_forbidden_if_not_users_report_report_delete(self):
        reportpk = Report.objects.get(ref_number='B123', doctor__user__username='testuser12').pk
        login = self.client.login(username='testuser11', password='12345')
        resp = self.client.get(reverse('report_delete_url', kwargs={'pk': reportpk}))

        self.assertEqual(resp.status_code, 403)

    def test_success_if_users_report_report_delete(self):
        reportpk = Report.objects.get(ref_number='A123', doctor__user__username='testuser11').pk
        login = self.client.login(username='testuser11', password='12345')
        resp = self.client.get(reverse('report_delete_url', kwargs={'pk': reportpk}))

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'reports/report_delete.html')

    def test_success_if_user_is_staff_and_not_users_report_report_delete(self):
        reportpk = Report.objects.get(ref_number='A123', doctor__user__username='testuser11').pk
        login = self.client.login(username='testuser12', password='12345')
        resp = self.client.get(reverse('report_delete_url', kwargs={'pk': reportpk}))

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'reports/report_delete.html')

        Report.objects.get(pk=reportpk).checked=True

    def test_forbidden_if_not_country_case_report_delete(self):
        reportpk = Report.objects.get(ref_number='D123', doctor__user__username='testuser11').pk
        login = self.client.login(username='testuser11', password='12345')
        resp = self.client.get(reverse('report_delete_url', kwargs={'pk': reportpk}))

        self.assertEqual(resp.status_code, 403)

        login = self.client.login(username='testuser12', password='12345')
        resp = self.client.get(reverse('report_delete_url', kwargs={'pk': reportpk}))

        self.assertEqual(resp.status_code, 403)

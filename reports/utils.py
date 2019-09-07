import os
from docxtpl import DocxTemplate, InlineImage
from docx.shared import Mm

from django.conf import settings
from .models import ReportTemplate
#from django.forms.models import model_to_dict

def DocReportGenerator(report):
    doc_path = ReportTemplate.objects.get(
            country=report.city.district.region.country, company=report.company
            ).template
    doc = DocxTemplate(doc_path)
    images = []
    for image in report.additional_images.get_queryset():
        images.append(InlineImage(doc, image.image, width=Mm(130)))

    context = {
    'ref_number': report.ref_number,
    'company_ref_number': report.company_ref_number,
    'company': report.company,
    'patients_first_name': report.patients_first_name,
    'patients_last_name': report.patients_last_name,
    'patients_date_of_birth': report.patients_date_of_birth,
    'patients_policy_number': report.patients_policy_number,
    'date_of_visit': report.date_of_visit,
    'city': report.city,
    'cause': report.cause_of_visit,
    'checkup': report.checkup,
    'additional_checkup': report.additional_checkup,
    'diagnosis': report.diagnosis.get_queryset(),
    'prescription': report.prescription,
    'doctor': report.doctor,
    'services': report.service_items.get_queryset(),
    'total_price': report.get_total_price,
    'images': images
    }


    doc.render(context)
    file_path = os.path.join(
                    settings.MEDIA_ROOT,
                    'FILES',
                    str(report.company),
                    str(report.doctor),
                    str(report),
                    "_".join((report.ref_number, report.patients_last_name, report.patients_first_name)) + '.docx'
                )
    doc.save(file_path)
    report.docx_download_link = os.path.join('/media',
                    'FILES',
                    str(report.company),
                    str(report.doctor),
                    str(report),
                    "_".join((report.ref_number, report.patients_last_name, report.patients_first_name)) + '.docx'
                ).replace(' ', '%20')
    report.save()
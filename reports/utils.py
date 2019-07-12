import os
from docxtpl import DocxTemplate, InlineImage
from docx.shared import Mm

from django.conf import settings

def DocReportGenerator(report):
    doc = DocxTemplate(os.path.join(settings.MEDIA_ROOT, 'DOC_TEMPLATES', 'LDM_template.docx'))
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
    'patients_passport_number': report.patients_passport_number,
    'date_of_visit': report.date_of_visit,
    'location': report.location,
    'cause': report.cause,
    'checkup': report.checkup,
    'additional_checkup': report.additional_checkup,
    'diagnosis': report.diagnosis.get_queryset(),
    'prescription': report.prescription,
    'doctor': report.doctor,
    'second_visit': report.second_visit,
    'services': report.service_items.get_queryset(),
    'total_price': report.get_total_price,
    'images': images
    }
    doc.render(context)
    doc.save(os.path.join(
                    settings.MEDIA_ROOT,
                    'FILES',
                    str(report.company),
                    str(report.doctor),
                    str(report),
                    "_".join((report.ref_number, report.patients_last_name, report.patients_first_name)) + '.docx'
                ))

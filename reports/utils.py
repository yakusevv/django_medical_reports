import os
from docxtpl import DocxTemplate, InlineImage
from docx.shared import Mm

from django.conf import settings
from .models import ReportTemplate
#from django.forms.models import model_to_dict

def DocReportGenerator(report):
    try:
        doc_path = ReportTemplate.objects.get(
            country=report.city.district.region.country, company=report.company
            ).template
        doc = DocxTemplate(doc_path)
        images = []
        for image in report.additional_images.get_queryset():
            images.append(InlineImage(doc, image.image, width=Mm(130)))

        context = {
                    'r': report,
                    'i': images,
                    'd': report.diagnosis.get_queryset(),
                    's': report.service_items.get_queryset()
                }

        doc.render(context)

        file_name = "_".join((
                            report.ref_number,
                            report.patients_last_name,
                            report.patients_first_name
                            )) + '.docx'

        file_local_dir = os.path.join(
                            'FILES',
                            str(report.pk)
                            )

        file_full_path = os.path.join(
                            settings.MEDIA_ROOT,
                            str(file_local_dir),
                            str(file_name)
                            )

        if not os.path.exists(file_full_path):
            os.makedirs(os.path.join(settings.MEDIA_ROOT,str(file_local_dir)))
        doc.save(file_full_path)

        report.docx_download_link = os.path.join(
                            settings.MEDIA_URL,
                            file_local_dir,
                            file_name,
                            ).replace(' ', '%20')

        report.save()

    except ReportTemplate.DoesNotExist:
            pass

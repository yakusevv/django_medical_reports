import os
from docxtpl import DocxTemplate, InlineImage
from docx.shared import Mm

from django.conf import settings


def DocReportGenerator(doc_path, report):
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

        file_system_dir = os.path.join(
                            settings.MEDIA_ROOT,
                            file_local_dir
                            )

        file_full_path = os.path.join(
                            settings.MEDIA_ROOT,
                            str(file_local_dir),
                            str(file_name)
                            )

        file_url_path = os.path.join(
                            settings.MEDIA_URL,
                            file_local_dir,
                            file_name
                            )

        if not os.path.exists(file_system_dir):
            os.makedirs(os.path.join(settings.MEDIA_ROOT, str(file_local_dir)))

        #past report deleting
        #in case when file name has changed
        try:
            os.remove(os.path.join(file_system_dir, report.docx_download_link.split('/')[-1]))
        except:
            pass

        doc.save(file_full_path)

        return file_url_path.replace(' ', '%20')

import os
from docxtpl import DocxTemplate, InlineImage
from docx.shared import Mm

from django.conf import settings

from .models import ReportTemplate

def DocReportGeneratorWithoutSaving(report, type):
    try:
        doc_path = ReportTemplate.objects.get(
            country=report.city.district.region.country
            ).template
        doc = DocxTemplate(doc_path)
        images = []
        for image in report.additional_images.get_queryset():
            images.append(InlineImage(doc, image.image, width=Mm(130)))

        context = {
                'r': report,
                'i': images,
                'd': report.diagnosis.get_queryset(),
                's': report.service_items.get_queryset(),
                't': type
                }
        doc.render(context)

        return doc
    except ReportTemplate.DoesNotExist:
        return None

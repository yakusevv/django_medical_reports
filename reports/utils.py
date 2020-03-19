import os
from docxtpl import DocxTemplate, InlineImage
from docx.shared import Mm
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
from openpyxl.utils import get_column_letter

from django.conf import settings
from django.utils.translation import ugettext as _

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


def ReportsXlsxGenerator(reports):
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = 'Reports'

    columns = [
        _('ref. number'),
        _('Company'),
        _('Company ref. number'),
        _('Last name'),
        _('First name'),
        _('Date of birth'),
        _('City'),
        _('Region'),
        _('Doctor'),
        _('Total price for the doctor'),
        _('Total price')
    ]

    row_num = 2

    for col_num, column_title in enumerate(columns, 2):
        cell = worksheet.cell(row=row_num, column=col_num)
        cell.value = column_title
        cell.font = Font(bold=True)
        cell.border = Border(
                        bottom=Side(border_style='medium', color='FF000000'),
                        top=Side(border_style='medium', color='FF000000'),
                        left=Side(border_style='medium', color='FF000000'),
                        right=Side(border_style='medium', color='FF000000'),
                    )
        cell.fill = PatternFill(
                        start_color='f7f7f9',
                        end_color='f7f7f9',
                        fill_type='solid',
                    )
        col_letter = get_column_letter(col_num)
        if col_letter == 'B':
            column_dimensions = worksheet.column_dimensions[col_letter]
            column_dimensions.width = 20
        elif col_letter == 'C':
            column_dimensions = worksheet.column_dimensions[col_letter]
            column_dimensions.width = 15
        elif col_letter == 'D':
            column_dimensions = worksheet.column_dimensions[col_letter]
            column_dimensions.width = 15
        elif col_letter == 'E':
            column_dimensions = worksheet.column_dimensions[col_letter]
            column_dimensions.width = 20
        elif col_letter == 'F':
            column_dimensions = worksheet.column_dimensions[col_letter]
            column_dimensions.width = 15
        elif col_letter == 'G':
            column_dimensions = worksheet.column_dimensions[col_letter]
            column_dimensions.width = 15
        elif col_letter == 'H':
            column_dimensions = worksheet.column_dimensions[col_letter]
            column_dimensions.width = 20
        elif col_letter == 'I':
            column_dimensions = worksheet.column_dimensions[col_letter]
            column_dimensions.width = 20
        elif col_letter == 'J':
            column_dimensions = worksheet.column_dimensions[col_letter]
            column_dimensions.width = 10

    for report in reports:
        row_num += 1

        row = [
            report.get_full_ref_number,
            report.company.name,
            report.company_ref_number,
            report.patients_last_name,
            report.patients_first_name,
            report.patients_date_of_birth.strftime("%d.%m.%Y"),
            report.city.name,
            report.city.district.region.name,
            report.doctor.initials,
            report.get_total_price_doctor,
            report.get_total_price
        ]

        for col_num, cell_value in enumerate(row, 2):
            cell = worksheet.cell(row=row_num, column=col_num)
            cell.value = cell_value

    return workbook

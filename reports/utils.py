from docxtpl import DocxTemplate, InlineImage
from docx.shared import Mm
from openpyxl import Workbook
from openpyxl.styles import Font, Border, Side, PatternFill, Alignment
from openpyxl.utils import get_column_letter

from django.utils.translation import ugettext as _

from .models import ReportTemplate


def docx_report_generator(report, type_of_report):
    try:
        doc_path = ReportTemplate.objects.get(
            country=report.city.district.region.country
            ).template
        doc = DocxTemplate(doc_path)
        images = []
        for image in report.additional_images.get_queryset():
            if image.expand:
                images.append(InlineImage(doc, image.image, width=Mm(170)))
            else:
                images.append(InlineImage(doc, image.image, width=Mm(110)))

        context = {
                'R': report,
                'i': images,
                'd': report.diagnosis.get_queryset(),
                's': report.service_items.get_queryset(),
                't': type_of_report
                }
        doc.render(context)

        return doc
    except ReportTemplate.DoesNotExist:
        return None


def reports_xlsx_generator(reports):
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = 'Reports'

    columns = [
        _('ref. number'),
        _('Company ref. number'),
        _('Full name, date of birth'),
        _('City'),
        _('Total price\nfor the doctor'),
        _('Total\nprice')
    ]

    row_num = 2
    col_first = 2

    for col_num, column_title in enumerate(columns, col_first):
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
        cell.alignment = Alignment(wrapText=True)
        col_letter = get_column_letter(col_num)
        if col_letter == 'B':
            column_dimensions = worksheet.column_dimensions[col_letter]
            column_dimensions.width = 20
        elif col_letter == 'C':
            column_dimensions = worksheet.column_dimensions[col_letter]
            column_dimensions.width = 25
        elif col_letter == 'D':
            column_dimensions = worksheet.column_dimensions[col_letter]
            column_dimensions.width = 35
        elif col_letter == 'E':
            column_dimensions = worksheet.column_dimensions[col_letter]
            column_dimensions.width = 15
        elif col_letter == 'F':
            column_dimensions = worksheet.column_dimensions[col_letter]
            column_dimensions.width = 10
        elif col_letter == 'G':
            column_dimensions = worksheet.column_dimensions[col_letter]
            column_dimensions.width = 10

    for index, report in enumerate(reports):
        row_num += 1

        row = [
            report.get_full_ref_number,
            report.company_ref_number,
            ' '.join((
                    str(report.patients_last_name),
                    str(report.patients_first_name)
                    )) + ', ' + str(report.patients_date_of_birth.strftime("%d.%m.%Y")),
            report.city.name,
            report.get_total_price_doctor,
            report.get_total_price
        ]

        for col_num, cell_value in enumerate(row, col_first):
            cell = worksheet.cell(row=row_num, column=col_num)
            cell.number_format = '0.00'
            cell.value = cell_value
            if index == len(reports) - 1:
                if col_num == col_first:
                    cell.border = Border(
                        left=Side(border_style='medium', color='FF000000'),
                        bottom=Side(border_style='medium', color='FF000000')
                    )
                elif col_num == (len(row) - 1) + col_first:
                    cell.border = Border(
                        right=Side(border_style='medium', color='FF000000'),
                        bottom=Side(border_style='medium', color='FF000000')
                    )
                else:
                    cell.border = Border(
                        left=Side(border_style='thin', color='FF000000'),
                        right=Side(border_style='thin', color='FF000000'),
                        bottom=Side(border_style='medium', color='FF000000')
                    )
            else:
                if col_num == col_first:
                    cell.border = Border(
                        left=Side(border_style='medium', color='FF000000'),
                    )
                elif col_num == (len(row) - 1) + col_first:
                    cell.border = Border(
                        right=Side(border_style='medium', color='FF000000'),
                    )
                else:
                    cell.border = Border(
                        left=Side(border_style='thin', color='FF000000'),
                        right=Side(border_style='thin', color='FF000000')
                    )

    return workbook

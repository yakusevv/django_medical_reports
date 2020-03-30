from .models import Country, ReportRequest
import shutil



def list_of_countries(request):
    return { 'list_of_countries': Country.objects.all() }

def storage_information(request):
    if request.user.is_staff:
        total, used, free = shutil.disk_usage("/")
        percent = used / total * 100
        return {
            "storage_percent": "{:.2f} %".format(percent)
            }
    else:
        return {
            "storage_percent": None
            }


def report_requests_count(request):
    if request.user.is_authenticated:
        profile = request.user.profile
        if request.user.is_staff:
            total = ReportRequest.objects.filter(report=None, status='accepted')
        else:
            total = profile.reportrequest_set.all()
        return {"report_requests_count": len(total)}
    return {"report_requests_count": 0 }

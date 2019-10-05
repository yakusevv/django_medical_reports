from .models import Country
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

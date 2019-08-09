from .models import Country


def list_of_countries(request):
    return { 'list_of_countries': Country.objects.all() }

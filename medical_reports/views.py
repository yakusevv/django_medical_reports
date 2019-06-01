from django.shortcuts import redirect


def redirect_news(request):
    print(1)
    return redirect('news/', permanent=True)

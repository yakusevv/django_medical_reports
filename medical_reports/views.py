from django.shortcuts import redirect


def redirect_news(request):
    return redirect('news_list_url', permanent=True)

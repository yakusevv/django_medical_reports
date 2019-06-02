from django.urls import path

from .views import news_list, PostDetail, PostCreate, PostUpdate, PostDelete

urlpatterns = [
        path('', news_list, name='news_list_url'),
        path('post/create/', PostCreate.as_view(), name='post_create_url'),
        path('post/<int:pk>/', PostDetail.as_view(), name='post_detail_url'),
        path('post/<int:pk>/update/', PostUpdate.as_view(), name='post_update_url'),
        path('post/<int:pk>/delete/', PostDelete.as_view(), name='post_delete_url'),
        ]

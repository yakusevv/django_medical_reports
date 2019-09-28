from django.urls import path

from .views import PostList, PostDetail, PostCreate, PostUpdate, PostDelete

urlpatterns = [
        path('', PostList.as_view(), name='news_list_url'),
        path('post/create/', PostCreate.as_view(), name='post_create_url'),
        path('post/<int:pk>/', PostDetail.as_view(), name='post_detail_url'),
        path('post/<int:pk>/update/', PostUpdate.as_view(), name='post_update_url'),
        path('post/<int:pk>/delete/', PostDelete.as_view(), name='post_delete_url'),
        ]

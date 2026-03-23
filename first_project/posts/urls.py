from django.urls import path
from .views import PostListView, PostCreateView

app_name = 'posts'

urlpatterns = [
    # 掲示板のメイン画面
    path('', PostListView.as_view(), name='post_list'),
    # 掲示板の新規作成画面
    path('create/', PostCreateView.as_view(), name='post_create'),
]
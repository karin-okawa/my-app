from django.urls import path
from .views import PostListView, PostCreateView, PostLikeView, PostDeleteView

app_name = 'posts'

urlpatterns = [
    # 掲示板のメイン画面
    path('', PostListView.as_view(), name='post_list'),
    # 掲示板の新規作成画面
    path('create/', PostCreateView.as_view(), name='post_create'),
    # いいね機能
    path('<int:pk>/like/', PostLikeView.as_view(), name='post_like'),
    # 投稿削除
    path('<int:pk>/delete/', PostDeleteView.as_view(), name='post_delete'),    

]
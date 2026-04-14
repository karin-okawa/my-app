from django.urls import path  # URLパターン定義関数のインポート
from .views import PostListView, PostCreateView, PostLikeView, PostDeleteView  # このアプリ内のビュークラスのインポート

# URLの名前空間（テンプレートから 'posts:post_list' のように参照する際に使用）
app_name = 'posts'

urlpatterns = [
    # 掲示板のメイン画面
    path('', PostListView.as_view(), name='post_list'),
    # 投稿新規作成画面
    path('create/', PostCreateView.as_view(), name='post_create'),
    # いいね機能
    path('<int:pk>/like/', PostLikeView.as_view(), name='post_like'),
    # 投稿削除
    path('<int:pk>/delete/', PostDeleteView.as_view(), name='post_delete'),
]
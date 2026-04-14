from django.urls import path  # URLパターン定義関数のインポート
from . import views  # このアプリ内のビューのインポート

# URLの名前空間（テンプレートから 'portfolio:portfolio' のように参照する際に使用）
app_name = 'portfolio'

urlpatterns = [
    # ポートフォリオのトップ画面
    path('', views.index, name='portfolio'),
]
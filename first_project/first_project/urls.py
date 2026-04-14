"""
URL configuration for first_project project.
The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin  # 管理画面モジュールのインポート
from django.urls import path, include  # URLパターン定義関数のインポート
from django.conf import settings  # プロジェクト設定のインポート
from django.conf.urls.static import static  # 静的・メディアファイル配信関数のインポート

urlpatterns = [
    path('', include('portfolio.urls')),                                            # ポートフォリオアプリのURL
    path('admin/', admin.site.urls),                                                # 管理画面のURL
    path('accounts/', include('accounts.urls')),                                    # アカウント管理アプリのURL
    path('home/', include(('home.urls', 'home'), namespace='home')),                # ホームアプリのURL
    path('households/', include(('households.urls', 'households'), namespace='households')),  # 家計簿アプリのURL
    path('posts/', include(('posts.urls', 'posts'), namespace='posts')),            # 投稿アプリのURL
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# 開発環境でアップロードされた画像ファイルを配信できるようにする
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
from django.contrib import admin
from django.urls import path, include
# メディアファイルを開発環境で配信するための設定
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', include('portfolio.urls')),
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('home/', include(('home.urls', 'home'), namespace='home')),
    path('households/', include(('households.urls', 'households'), namespace='households')),
    path('posts/', include(('posts.urls', 'posts'), namespace='posts')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# 開発環境でアップロードされた画像ファイルを配信できるようにする
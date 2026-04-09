from django.urls import path
from django.contrib.auth import views as auth_views
from .views import (
    RegistUserView, UserLoginView, UserLogoutView, 
    MyPageView, LogoutDoneView, UserUpdateView, 
    AvatarUpdateView, NicknameUpdateView,
    EmailUpdateView, EmailUpdateDoneView, EmailConfirmView,
)
from django.contrib.auth.views import PasswordChangeView, PasswordChangeDoneView

app_name = 'accounts'

urlpatterns = [
    #　ユーザー登録・ログイン・ログアウト
    path('regist/', RegistUserView.as_view(), name='regist'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    
    # ログアウト完了画面
    path('logout/done/', LogoutDoneView.as_view(), name='logout_done'),

    # マイページ
    path('mypage/', MyPageView.as_view(), name='mypage'),

    # プロフィール編集
    path('update/', UserUpdateView.as_view(), name='user_update'),

    # パスワードリセット系
    path(
        'password_reset/',
        auth_views.PasswordResetView.as_view(
            template_name='accounts/password_reset_form.html',
            email_template_name = 'accounts/password_reset_email.txt',
            success_url='/accounts/password_reset/done/',
        ),
        name='password_reset',
    ),
    path(
        "password_reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="accounts/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="accounts/password_reset_confirm.html",
            success_url="/accounts/reset/done/",
        ),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="accounts/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
    
    path('avatar/update/', AvatarUpdateView.as_view(), name='avatar_update'),
    
    path('nickname/update/', NicknameUpdateView.as_view(), name='nickname_update'),

    path('email/update/', EmailUpdateView.as_view(), name='email_update'),
    
    path('email/update/done/', EmailUpdateDoneView.as_view(), name='email_update_done'),
    
    path('email/confirm/<str:token>/', EmailConfirmView.as_view(), name='email_confirm'),

    path('password/change/', PasswordChangeView.as_view(
        template_name='accounts/password_change.html',
        success_url='/accounts/password/change/done/',
    ), name='password_change'),

    path('password/change/done/', PasswordChangeDoneView.as_view(
        template_name='accounts/password_change_done.html',
        extra_context={'hide_nav': True},
    ), name='password_change_done'),
]
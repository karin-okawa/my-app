from django.urls import path  # URLパターン定義関数のインポート
from django.contrib.auth.views import (  # 認証関連のビュークラスのインポート
    PasswordChangeView, PasswordChangeDoneView,
    PasswordResetView, PasswordResetDoneView,
    PasswordResetConfirmView,
)
from .views import (  # このアプリ内のビュークラスのインポート
    RegistUserView, UserLoginView, UserLogoutView,
    MyPageView, LogoutDoneView, UserUpdateView,
    AvatarUpdateView, NicknameUpdateView,
    EmailUpdateView, EmailUpdateDoneView, EmailConfirmView,
    ReminderSettingView, PasswordResetCompleteView, EmailConfirmDoneView,
)

# URLの名前空間（テンプレートから 'accounts:login' のように参照する際に使用）
app_name = 'accounts'

urlpatterns = [
    # ユーザー登録
    path('regist/', RegistUserView.as_view(), name='regist'),
    # ログイン
    path('login/', UserLoginView.as_view(), name='login'),
    # ログアウト
    path('logout/', UserLogoutView.as_view(), name='logout'),
    # ログアウト完了画面
    path('logout/done/', LogoutDoneView.as_view(), name='logout_done'),
    # マイページ
    path('mypage/', MyPageView.as_view(), name='mypage'),
    # ユーザー情報更新
    path('update/', UserUpdateView.as_view(), name='user_update'),
    # プロフィール画像更新
    path('avatar/update/', AvatarUpdateView.as_view(), name='avatar_update'),
    # ニックネーム更新
    path('nickname/update/', NicknameUpdateView.as_view(), name='nickname_update'),
    # メールアドレス変更画面
    path('email/update/', EmailUpdateView.as_view(), name='email_update'),
    # メールアドレス変更後の確認画面
    path('email/update/done/', EmailUpdateDoneView.as_view(), name='email_update_done'),
    # メールアドレス変更確認リンク
    path('email/confirm/<str:token>/', EmailConfirmView.as_view(), name='email_confirm'),
    # メールアドレス変更完了画面
    path('email/confirm/done/', EmailConfirmDoneView.as_view(), name='email_confirm_done'),
    # パスワード変更画面（ログイン済み）
    path('password/change/', PasswordChangeView.as_view(
        template_name='accounts/password_change.html',
        success_url='/accounts/password/change/done/',
    ), name='password_change'),
    # パスワード変更完了画面
    path('password/change/done/', PasswordChangeDoneView.as_view(
        template_name='accounts/password_change_done.html',
        extra_context={'hide_nav': True},
    ), name='password_change_done'),
    # パスワードリセット（メール送信）
    path('password_reset/', PasswordResetView.as_view(
        template_name='accounts/password_reset_form.html',
        email_template_name='accounts/password_reset_email.txt',
        subject_template_name='accounts/password_reset_subject.txt',
        success_url='/accounts/password_reset/done/',
    ), name='password_reset'),
    # パスワードリセットメール送信完了画面
    path('password_reset/done/', PasswordResetDoneView.as_view(
        template_name='accounts/password_reset_done.html'
    ), name='password_reset_done'),
    # パスワードリセット確認リンク
    path('reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(
        template_name='accounts/password_reset_confirm.html',
        success_url='/accounts/reset/done/',
        extra_context={'hide_nav': True},  # ヘッダー・フッターを非表示にする
    ), name='password_reset_confirm'),
    # パスワードリセット完了画面
    path('reset/done/', PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    # リマインダー設定画面
    path('reminder/', ReminderSettingView.as_view(), name='reminder_setting'),
]
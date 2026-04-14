from django.db import models  # Djangoのモデルモジュールのインポート
from django.contrib.auth.models import (
    # ユーザー生成・パスワードハッシュ化・権限管理のための各ベースクラス
    BaseUserManager, AbstractBaseUser, PermissionsMixin
)
from django.urls import reverse_lazy  # 名前付きURLパターンからURLを動的に生成する関数のインポート


# ユーザー生成ロジックを定義するマネジャークラス
class UserManager(BaseUserManager):

    # 一般ユーザー作成メソッド
    def create_user(self, username, email, password):
        if not email:
            raise ValueError('メールアドレスを入力してください')
        if not password:
            raise ValueError('パスワードを入力してください')
        user = self.model(
            username=username,
            # メールアドレスの正規化（表記ゆれの修正）
            email=self.normalize_email(email)
        )
        # パスワードのハッシュ化および設定
        user.set_password(password)
        # データベースへの保存
        user.save()
        return user


# 実際のユーザーモデル本体（メールアドレスでのログインに対応）
class User(AbstractBaseUser, PermissionsMixin):
    # ユーザー名
    username = models.CharField(max_length=25)
    # メールアドレス（一意性を確保）
    email = models.EmailField(max_length=100, unique=True)
    # アカウントの有効状態
    is_active = models.BooleanField(default=True)
    # 管理画面へのアクセス権限
    is_staff = models.BooleanField(default=False)
    # プロフィール画像
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    # リマインダー通知時間
    reminder_time = models.TimeField(null=True, blank=True)
    # リマインダー通知の有効化フラグ
    reminder_enabled = models.BooleanField(default=False)
    # 励ましメッセージ機能の有効化フラグ
    encourage_enabled = models.BooleanField(default=False)
    # レコードの作成日時
    created_at = models.DateTimeField(auto_now_add=True)
    # レコードの最終更新日時
    updated_at = models.DateTimeField(auto_now=True)
    # ログインに使用する識別フィールドの指定
    USERNAME_FIELD = 'email'
    # ユーザー作成時に必須となるフィールド
    REQUIRED_FIELDS = ['username']
    # カスタムマネジャーの適用
    objects = UserManager()

    # オブジェクト詳細ページのURLを返却するメソッド
    def get_absolute_url(self):
        return reverse_lazy('home:home')
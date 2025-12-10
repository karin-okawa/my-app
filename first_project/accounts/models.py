from django.db import models
from django.contrib.auth.models import(
    # ユーザー生成処理を書くためのクラス、パスワードのハッシュ化やログイン機能などを持つクラス、権限（is_superuserやgroupsなど）を持たせるためのクラス
    BaseUserManager, AbstractBaseUser, PermissionsMixin
)
from django.urls import reverse_lazy

# ユーザーを作る方法を定義するクラス（今回はcreate_user)
class UserManager(BaseUserManager):
    def create_user(self, username, email, password):
        if not email:
            raise ValueError('メールアドレスを入力してください')
        if not password:
            raise ValueError('パスワードを入力してください')
        user = self.model(
            username=username,
            # メールアドレスの表記ゆれを整える関数（大文字→小文字など）
            email=self.normalize_email(email)     
        )
        # パスワードをハッシュ化して保存する
        user.set_password(password)
        # DBに保存する
        user.save()
        return user

# Userが実際のユーザーモデル本体を表す（メールログイン対応） 
# AbstractBaseUserはログイン機能・パスワードハッシュなどを提供
# PermissionsMixinはis_superuser,groups,user_permissionsを提供し、管理画面の権限システムを使えるようにしてくれるクラス
class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=25)
    email = models.EmailField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)
    # 管理画面に入れるかどうか
    is_staff = models.BooleanField(default=False)
    
    # ログインIDとしてユーザー名ではなくメールアドレスを設定してる
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    # User.objectsを使った時にUserManagerが動く設定
    objects = UserManager()
    
    # get_absolute_urlがユーザー登録後などに遷移するurlを渡す
    def get_absolute_url(self):
        return reverse_lazy('accounts:home')
    
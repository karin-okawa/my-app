from django import forms  # Djangoのフォームモジュールのインポート
from django.contrib.auth import authenticate  # ユーザー認証関数のインポート
from django.contrib.auth.password_validation import validate_password  # パスワードバリデーション関数のインポート
from django.contrib.auth import get_user_model  # カスタムユーザーモデル取得関数のインポート

# カスタムユーザーモデルの取得
User = get_user_model()

class RegistForm(forms.ModelForm):
    # パスワード入力フィールド
    password1 = forms.CharField(
        label='パスワード',
        widget=forms.PasswordInput()
    )
    # パスワード再入力フィールド（確認用）
    password2 = forms.CharField(
        label='パスワード（確認）',
        widget=forms.PasswordInput()
    )

    class Meta:
        # 使用するモデルの指定
        model = User
        # フォームに表示するフィールド
        fields = ['username', 'email']
        # ラベルの設定
        labels = {
            'username': 'ニックネーム',
            'email': 'メールアドレス',
        }

    # パスワード一致確認のバリデーション処理
    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password1')
        p2 = cleaned_data.get('password2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError('パスワードが一致しません')
        return cleaned_data

    # ユーザー保存処理
    def save(self, commit=True):
        # インスタンス生成（DBへの保存は保留）
        user = super().save(commit=False)
        # 入力されたパスワードの取得
        password = self.cleaned_data.get('password1')
        # パスワードの強度チェック（バリデーション実行）
        validate_password(password, user)
        # パスワードのハッシュ化処理
        user.set_password(password)
        if commit:
            # データベースへの保存実行
            user.save()
        return user


class UserLoginForm(forms.Form):
    # ログイン用メールアドレス入力フィールド
    email = forms.EmailField(label='メールアドレス')
    # ログイン用パスワード入力フィールド
    password = forms.CharField(
        label='パスワード',
        widget=forms.PasswordInput()
    )

    # 認証情報のバリデーション処理
    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')
        # 入力された情報に基づいたユーザー認証の実行
        user = authenticate(email=email, password=password)
        if user is None:
            raise forms.ValidationError('メールアドレスまたはパスワードが違います')
        # 認証済みユーザーオブジェクトの格納
        cleaned_data['user'] = user
        return cleaned_data
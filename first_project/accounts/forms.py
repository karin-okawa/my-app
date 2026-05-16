from django import forms  # Djangoのフォームモジュールのインポート
from django.contrib.auth import authenticate  # ユーザー認証関数のインポート
from django.contrib.auth.password_validation import validate_password  # パスワード強度チェック関数のインポート
from django.contrib.auth import get_user_model  # カスタムユーザーモデル取得関数のインポート
from django.contrib.auth.forms import PasswordChangeForm  # Djangoの組み込みパスワード変更フォームのインポート


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
        model = User
        fields = ['username', 'email']
        labels = {
            'username': 'ニックネーム',
            'email': 'メールアドレス',
        }

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password1')
        p2 = cleaned_data.get('password2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError('パスワードが一致しません')
        if p1:
            if len(p1) < 12:
                self.add_error('password1', '12文字以上で入力してください')
            if not any(c.isupper() for c in p1):
                self.add_error('password1', '英大文字を1文字以上含めてください')
            if not any(c.islower() for c in p1):
                self.add_error('password1', '英小文字を1文字以上含めてください')
            if not any(c.isdigit() for c in p1):
                self.add_error('password1', '数字を1文字以上含めてください')
            if not any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in p1):
                self.add_error('password1', '記号（!@#$%など）を1文字以上含めてください')
        return cleaned_data

    # ユーザー保存処理（← cleanと同じインデント、クラスの中）
    def save(self, commit=True):
        # インスタンス生成（DBへの保存は保留）
        user = super().save(commit=False)
        # パスワードのハッシュ化処理
        user.set_password(self.cleaned_data.get('password1'))
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
    

# パスワード変更フォーム（カスタムバリデーション付き）
class CustomPasswordChangeForm(PasswordChangeForm):
    def clean_new_password1(self):
        # 新しいパスワードのバリデーションを行う
        p1 = self.cleaned_data.get('new_password1')
        if p1:
            # 12文字以上チェック
            if len(p1) < 12:
                raise forms.ValidationError('12文字以上で入力してください')
            # 英大文字チェック
            if not any(c.isupper() for c in p1):
                raise forms.ValidationError('英大文字を1文字以上含めてください')
            # 英小文字チェック
            if not any(c.islower() for c in p1):
                raise forms.ValidationError('英小文字を1文字以上含めてください')
            # 数字チェック
            if not any(c.isdigit() for c in p1):
                raise forms.ValidationError('数字を1文字以上含めてください')
            # 記号チェック
            if not any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in p1):
                raise forms.ValidationError('記号（!@#$%など）を1文字以上含めてください')
        return p1
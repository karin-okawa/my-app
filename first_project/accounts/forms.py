from django import forms
from .models import User
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import get_user_model

User = get_user_model()

class RegistForm(forms.ModelForm):
    password1 = forms.CharField(
        label='パスワード',
        widget=forms.PasswordInput()
    )
    password2 = forms.CharField(
        label='パスワード（確認）',
        widget=forms.PasswordInput()
    )
    
    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'password': forms.PasswordInput(),
        }
        labels = {
            'username': '名前',
            'email' : 'メールアドレス',
        }
   
    #パスワードが一致してるかの確認
    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password1')
        p2 = cleaned_data.get('password2')
        
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError('パスワードが一致しません')
        
        return cleaned_data
    
    #保存処理 
    def save(self, commit=True):
        user = super().save(commit=False)
        
        #バリデーション（強度チェック）
        validate_password(self.cleaned_data['password'], user)
        #ハッシュ化して保存
        user.set_password(self.cleaned_data['password'])
        
        if commit:
            user.save()
        return user
    

class UserLoginForm(forms.Form):
    email = forms.EmailField(label='メールアドレス')
    password = forms.CharField(
        label='パスワード',
        widget=forms.PasswordInput()
    )
    
    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')
        
        user = authenticate(email=email, password=password)
        
        if user is None:
            raise forms.ValidationError('メールアドレスまたはパスワードが違います')
        
        cleaned_data['user'] = user
        return cleaned_data
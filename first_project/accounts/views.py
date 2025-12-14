from django.shortcuts import render
from django.views.generic import(
    TemplateView, CreateView, FormView, View
)
from django.urls import reverse_lazy
from .forms import RegistForm

class HomeView(TemplateView):
# ただ画面を表示するだけの処理に適したView
    template_name = 'home.html'
    
class RegistUserView(CreateView):
# ユーザー登録のView（フォーム入力→バリデーション→DB保存まで）
    template_name = 'regist.html'
# 使用するフォーム
    form_class = RegistForm
    success_url = reverse_lazy('accounts:home')
    
class UserLoginView(FormView):
    template_name = 'login.html'
    
class UserLogoutView(View):
    pass
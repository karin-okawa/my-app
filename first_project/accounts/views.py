from django.shortcuts import render, redirect
from django.views.generic import(
    CreateView, FormView, View
)
from django.urls import reverse_lazy
from django.contrib.auth import authenticate, login, logout
from .forms import RegistForm, UserLoginForm

    
class RegistUserView(CreateView):
# ユーザー登録のView（フォーム入力→バリデーション→DB保存まで）
    template_name = 'accounts/regist.html'
# 使用するフォーム
    form_class = RegistForm
    success_url = reverse_lazy('accounts:login')
    
class UserLoginView(FormView):
    template_name = 'accounts/login.html'
    form_class = UserLoginForm
    success_url = reverse_lazy('home:home')
    
    def form_valid(self, form):
        user = form.cleaned_data['user']
        login(self.request, user)
        return super().form_valid(form)
    
class UserLogoutView(View):
    def get(self,request, *args, **kwargs):
        return render(request, 'accounts/logout.html')
    
    def post(self, request, *args, **kwargs):
        logout(request)
        return redirect('accounts:login')
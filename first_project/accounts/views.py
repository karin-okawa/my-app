from django.shortcuts import render, redirect
from django.views.generic import(
    CreateView, FormView, View, UpdateView, DetailView, TemplateView
)
from django.urls import reverse_lazy
from django.contrib.auth import login, logout
from .forms import RegistForm, UserLoginForm
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import User
from django.http import JsonResponse


# ユーザー登録
class RegistUserView(CreateView):
    template_name = 'accounts/regist.html'
    form_class = RegistForm
    success_url = reverse_lazy('accounts:login')

# ログイン 
class UserLoginView(FormView):
    template_name = 'accounts/login.html'
    form_class = UserLoginForm
    success_url = reverse_lazy('home:home')
    
    def form_valid(self, form):
        user = form.cleaned_data['user']
        # forms.py でパスワード照合が済んだユーザーを取りだす
        login(self.request, user)
        # ブラウザに「この人はログイン中ですよ」というクッキー（セッション）を保存させる
        return super().form_valid(form)
        # 最終的に success_url（ホーム画面など）へリダイレクトさせる

# マイページ（詳細表示） 
class MyPageView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'accounts/mypage.html'
    context_object_name = 'user_obj'
   
    def get_object(self):
        # URLのpkではなく、現在ログインしているユーザー自身を編集対象にする
        return self.request.user
    
# ログアウト処理（実行のみ）
class UserLogoutView(View):
    def post(self, request, *args, **kwargs):
        logout(request)
        return redirect('accounts:logout_done')
    
# ログアウト完了画面（表示のみ）
class LogoutDoneView(TemplateView):
    template_name ='accounts/logout.html'
    
# プロフィール編集
class UserUpdateView(LoginRequiredMixin, UpdateView):
    # ログイン済みユーザーのみアクセス可能にするMixin
    model = User
    template_name = 'accounts/user_update.html'
    # 編集を許可するフィールドを指定する
    fields = ['username', 'email'] 
    success_url = reverse_lazy('accounts:mypage') # マイページへ戻す

    def get_object(self):
        # URLのpkではなく、現在ログインしているユーザー自身を編集対象にする
        return self.request.user


# プロフィール画像更新
class AvatarUpdateView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        # アップロードされた画像をユーザーのavatarに保存する
        user = request.user
        if 'avatar' in request.FILES:
            user.avatar = request.FILES['avatar']
            user.save()
        return redirect('accounts:mypage')

# ニックネーム更新
class NicknameUpdateView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        # 送信されたニックネームを保存する
        user = request.user
        username = request.POST.get('username', '').strip()
        if username:
            user.username = username
            user.save()
        return redirect('accounts:mypage')
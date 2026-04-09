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


from django.core.mail import send_mail
from django.contrib.auth.hashers import check_password
import uuid
from django.utils import timezone
from datetime import timedelta


from households.models import HouseholdAccount, UserHouseholdAccount

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
        
        # ログイン時に家計簿がなければ「個人家計簿」を自動作成する
        if not UserHouseholdAccount.objects.filter(user=user).exists():
            household = HouseholdAccount.objects.create(name='個人家計簿')
            UserHouseholdAccount.objects.create(
                user=user,
                household_account=household,
                status=1,
                joined_at=timezone.now()
            )
            
            # デフォルトカテゴリーを作成する
            default_categories = [
                # 支出カテゴリー
                {'name': '食費', 'category_type': 'expense', 'color': '#e74c3c', 'order': 1},
                {'name': '日用品費', 'category_type': 'expense', 'color': '#e67e22', 'order': 2},
                {'name': '衣服費', 'category_type': 'expense', 'color': '#f1c40f', 'order': 3},
                {'name': '交通費', 'category_type': 'expense', 'color': '#2ecc71', 'order': 4},
                {'name': '趣味費', 'category_type': 'expense', 'color': '#3498db', 'order': 5},
                {'name': '交際費', 'category_type': 'expense', 'color': '#9b59b6', 'order': 6},
                {'name': '固定費', 'category_type': 'expense', 'color': '#2c3e50', 'order': 7},
                {'name': 'その他', 'category_type': 'expense', 'color': '#95a5a6', 'order': 8},
                # 収入カテゴリー
                {'name': '給与', 'category_type': 'income', 'color': '#2ecc71', 'order': 1},
                {'name': 'その他', 'category_type': 'income', 'color': '#95a5a6', 'order': 2},
            ]
            for cat in default_categories:
                Category.objects.create(
                    household_account=household,
                    **cat
                )
            
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
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # テンプレートでuser_objとして参照できるようにする
        context['user_obj'] = self.request.user
        return context



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
    
    

# メールアドレス変更画面
class EmailUpdateView(LoginRequiredMixin, View):
    template_name = 'accounts/email_update.html'

    def get(self, request, *args, **kwargs):
        # GETリクエスト時はフォーム画面を表示する
        return render(request, self.template_name, {'user_obj': request.user})

    def post(self, request, *args, **kwargs):
        new_email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()

        # パスワードの確認
        if not request.user.check_password(password):
            return render(request, self.template_name, {
                'user_obj': request.user,
                'error': 'パスワードが正しくありません'
            })

        # メールアドレスの重複確認
        if User.objects.filter(email=new_email).exclude(pk=request.user.pk).exists():
            return render(request, self.template_name, {
                'user_obj': request.user,
                'error': 'このメールアドレスはすでに使用されています'
            })

        # 確認トークンを生成してセッションに保存する
        token = str(uuid.uuid4())
        request.session['email_change_token'] = token
        request.session['email_change_new'] = new_email
        request.session['email_change_expires'] = str(timezone.now() + timedelta(minutes=30))

        # 確認メールを送信する
        confirm_url = request.build_absolute_uri(f'/accounts/email/confirm/{token}/')
        send_mail(
            subject='メールアドレス変更の確認',
            message=f'以下のリンクをクリックしてメールアドレスの変更を完了してください。\n\n{confirm_url}\n\n※このリンクの有効期限は30分です。',
            from_email=None,
            recipient_list=[new_email],
        )

        return redirect('accounts:email_update_done')


# メールアドレス変更後の確認画面
class EmailUpdateDoneView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/email_update_done.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 送信先メールアドレスをテンプレートに渡す
        context['new_email'] = self.request.session.get('email_change_new', '')
        # ヘッダー・フッターを非表示にする
        context['hide_nav'] = True
        return context


# メールアドレス変更確認リンクの処理
class EmailConfirmView(LoginRequiredMixin, View):
    def get(self, request, token, *args, **kwargs):
        session_token = request.session.get('email_change_token')
        new_email = request.session.get('email_change_new')
        expires_str = request.session.get('email_change_expires')

        # トークンの検証
        if not session_token or session_token != token:
            return render(request, 'accounts/email_confirm_error.html', {
                'error': 'リンクが無効です',
                'hide_nav': True,  # ヘッダー・フッターを非表示にする
            })

        # 有効期限の確認
        if timezone.now() > expires:
            return render(request, 'accounts/email_confirm_error.html', {
                'error': 'リンクの有効期限が切れています',
                'hide_nav': True,  # ヘッダー・フッターを非表示にする
            })
                

        # メールアドレスを更新する
        request.user.email = new_email
        request.user.save()

        # セッションをクリアする
        del request.session['email_change_token']
        del request.session['email_change_new']
        del request.session['email_change_expires']

        return redirect('accounts:mypage')
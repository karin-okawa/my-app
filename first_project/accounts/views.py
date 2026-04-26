# ①Django標準機能
from django.shortcuts import render, redirect  # 画面描画とリダイレクトのインポート
from django.views.generic import (  # 汎用ビュークラスのインポート
    CreateView, FormView, View, UpdateView, DetailView, TemplateView
)
from django.contrib.auth import login, logout  # ログイン・ログアウト関数のインポート
from django.contrib.auth.mixins import LoginRequiredMixin  # ログイン必須Mixinのインポート
from django.urls import reverse_lazy  # 名前付きURLパターンからURLを動的に生成する関数のインポート
from django.http import JsonResponse  # JSONレスポンス生成クラスのインポート
from django.core.mail import send_mail  # メール送信関数のインポート
from django.utils import timezone  # タイムゾーン対応の日時取得モジュールのインポート
from django.utils.dateparse import parse_datetime  # 文字列から日時オブジェクトへの変換関数のインポート

# ②このアプリ内のモデルとフォーム
from .forms import RegistForm, UserLoginForm  # このアプリ内のフォームクラスのインポート
from .models import User  # このアプリ内のユーザーモデルのインポート

# ③その他のライブラリ
from django.contrib.auth.hashers import check_password  # パスワードハッシュ照合関数のインポート
import uuid  # ランダムなトークン生成モジュールのインポート
from datetime import timedelta  # 時間差分を扱うクラスのインポート

# ④他アプリのモデル
from households.models import HouseholdAccount, UserHouseholdAccount, Category  # 家計簿アプリのモデルのインポート


# ユーザー登録ビュー
class RegistUserView(CreateView):
    template_name = 'accounts/regist.html'
    form_class = RegistForm
    success_url = reverse_lazy('accounts:login')


# ログインビュー
class UserLoginView(FormView):
    template_name = 'accounts/login.html'
    form_class = UserLoginForm
    success_url = reverse_lazy('home:home')
    
    def dispatch(self, request, *args, **kwargs):
        # すでにログイン済みの場合はホーム画面へリダイレクトする
        if request.user.is_authenticated:
            return redirect('home:home')
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        # forms.pyでパスワード照合が済んだユーザーを取り出す
        user = form.cleaned_data['user']
        login(self.request, user)

        # 招待トークンがセッションにある場合は参加処理へ飛ばす
        invite_token = self.request.session.pop('invite_token', None)
        if invite_token:
            return redirect('home:household_join', token=invite_token)

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

        # 最終的にsuccess_url（ホーム画面）へリダイレクトさせる
        return super().form_valid(form)
        

# パスワードリセット完了後にログアウトしてログイン画面へ遷移するビュー
class PasswordResetCompleteView(TemplateView):
    template_name = 'accounts/password_reset_complete.html'

    def get(self, request, *args, **kwargs):
        # ログイン済みの場合はログアウトする
        if request.user.is_authenticated:
            logout(request)
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # ヘッダー・フッターを非表示にする
        context['hide_nav'] = True
        return context


# マイページビュー（ログインユーザー自身の情報を表示）
class MyPageView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'accounts/mypage.html'
    context_object_name = 'user_obj'

    def get_object(self):
        # URLのpkではなく、現在ログインしているユーザー自身を表示対象にする
        return self.request.user


# ログアウト処理ビュー（実行のみ）
class UserLogoutView(View):
    def post(self, request, *args, **kwargs):
        logout(request)
        return redirect('accounts:logout_done')


# ログアウト完了画面ビュー（表示のみ）
class LogoutDoneView(TemplateView):
    template_name = 'accounts/logout.html'


# ユーザー情報編集ビュー
class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = 'accounts/user_update.html'
    # 編集を許可するフィールドの指定
    fields = ['username', 'email']
    success_url = reverse_lazy('accounts:mypage')

    def get_object(self):
        # URLのpkではなく、現在ログインしているユーザー自身を編集対象にする
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # テンプレートでuser_objとして参照できるようにする
        context['user_obj'] = self.request.user
        return context


# プロフィール画像更新ビュー
class AvatarUpdateView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        user = request.user
        if 'avatar' in request.FILES:
            # アップロードされた画像をユーザーのavatarに保存する
            user.avatar = request.FILES['avatar']
            user.save()
        return redirect('accounts:mypage')


# ニックネーム更新ビュー
class NicknameUpdateView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        user = request.user
        # 送信されたニックネームを取得し、前後の空白を除去する
        username = request.POST.get('username', '').strip()
        if username:
            user.username = username
            user.save()
        return redirect('accounts:mypage')


# メールアドレス変更ビュー
class EmailUpdateView(LoginRequiredMixin, View):
    template_name = 'accounts/email_update.html'

    def get(self, request, *args, **kwargs):
        # GETリクエスト時はフォーム画面を表示する
        return render(request, self.template_name, {'user_obj': request.user})

    def post(self, request, *args, **kwargs):
        # 入力値の取得と前後の空白除去
        new_email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()

        # パスワードの確認
        if not request.user.check_password(password):
            return render(request, self.template_name, {
                'user_obj': request.user,
                'error': 'パスワードが正しくありません'
            })

        # 現在と同じメールアドレスの確認
        if new_email == request.user.email:
            return render(request, self.template_name, {
                'user_obj': request.user,
                'error': '現在と同じメールアドレスです。別のメールアドレスを入力してください'
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

        # 確認メールを送信する（エラーが出ても次の画面に進む）
        try:
            confirm_url = request.build_absolute_uri(f'/accounts/email/confirm/{token}/')
            send_mail(
                subject='【かけいまもるくん】メールアドレス変更の確認',
                message=f'メールアドレス変更のリンクです：\n{confirm_url}\nこのメールに心当たりがない場合は破棄してください。',
                from_email=None,
                recipient_list=[new_email],
            )
        except Exception as e:
            print("メール送信エラー:", e)

        return redirect('accounts:email_update_done')


# メールアドレス変更後の確認画面ビュー
class EmailUpdateDoneView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/email_update_done.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 送信先メールアドレスをテンプレートに渡す
        context['new_email'] = self.request.session.get('email_change_new', '')
        # ヘッダー・フッターを非表示にする
        context['hide_nav'] = True
        return context


# メールアドレス変更確認リンクの処理ビュー
class EmailConfirmView(LoginRequiredMixin, View):
    def get(self, request, token, *args, **kwargs):
        # セッションから確認用データを取得する
        session_token = request.session.get('email_change_token')
        new_email = request.session.get('email_change_new')
        expires_str = request.session.get('email_change_expires')

        # トークンの検証
        if not session_token or session_token != token:
            return render(request, 'accounts/email_confirm_error.html', {
                'error': 'リンクが無効です',
                'hide_nav': True,  # ヘッダー・フッターを非表示にする
            })

        # 有効期限の確認（文字列を日時オブジェクトに変換してから比較する）
        expires = parse_datetime(expires_str)
        if timezone.now() > expires:
            return render(request, 'accounts/email_confirm_error.html', {
                'error': 'リンクの有効期限が切れています',
                'hide_nav': True,  # ヘッダー・フッターを非表示にする
            })

        # メールアドレスを更新する
        request.user.email = new_email
        request.user.save()

        # 使用済みセッションデータの削除
        del request.session['email_change_token']
        del request.session['email_change_new']
        del request.session['email_change_expires']

        # メールアドレス変更完了後はログアウトして完了画面へ遷移する
        logout(request)
        return redirect('accounts:email_confirm_done')


# メールアドレス変更完了画面ビュー
class EmailConfirmDoneView(TemplateView):
    template_name = 'accounts/email_confirm_done.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # ヘッダー・フッターを非表示にする
        context['hide_nav'] = True
        return context


# リマインダー設定ビュー
class ReminderSettingView(LoginRequiredMixin, View):
    template_name = 'accounts/reminder_setting.html'

    def get(self, request, *args, **kwargs):
        # 現在の設定を表示する
        return render(request, self.template_name, {'user_obj': request.user})

    def post(self, request, *args, **kwargs):
        user = request.user
        # リマインダーのON/OFFを保存する
        user.reminder_enabled = request.POST.get('reminder_enabled') == 'on'
        # 励ましメッセージのON/OFFを保存する
        user.encourage_enabled = request.POST.get('encourage_enabled') == 'on'
        # リマインダー時刻を保存する（未入力の場合はNoneを設定）
        reminder_time = request.POST.get('reminder_time', '').strip()
        if reminder_time:
            user.reminder_time = reminder_time
        else:
            user.reminder_time = None
        user.save()
        return redirect('accounts:reminder_setting')
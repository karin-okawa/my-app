# ①Django標準機能
from django.shortcuts import render  # 画面描画関数のインポート
from django.views.generic import ListView, CreateView, DeleteView  # 汎用ビュークラスのインポート
from django.contrib.auth.mixins import LoginRequiredMixin  # ログイン必須Mixinのインポート
from django.urls import reverse_lazy  # 名前付きURLパターンからURLを動的に生成する関数のインポート
from django.http import JsonResponse  # JSONレスポンス生成クラスのインポート
from django.views import View  # Viewの基本クラスのインポート
from django.db.models import Sum  # DB集計用（合計）関数のインポート
from django.utils import timezone  # タイムゾーン対応の日時取得モジュールのインポート

# ②このアプリ内のモデルとフォーム
from .models import Post  # このアプリ内の投稿モデルのインポート
from .forms import PostForm  # このアプリ内のフォームクラスのインポート

# ③他アプリのモデルと関数
from households.models import Transaction, Category  # 家計簿アプリのモデルのインポート
from home.views import get_current_household  # 現在選択中の家計簿を取得する関数のインポート


# ============================
# 掲示板一覧ビュー
# ============================
class PostListView(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'posts/post_list.html'
    context_object_name = 'all_posts'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # モーダル内の入力項目を表示するための空フォームを渡す
        context['form'] = PostForm()
        # 現在の年月をデフォルト値として渡す
        now = timezone.now()
        context['current_year'] = now.year
        context['current_month'] = now.month
        # 現在の家計簿に紐づいた自分の投稿だけを最新順で取得する
        household = get_current_household(self.request)
        context['my_posts'] = Post.objects.filter(
            user=self.request.user,
            household=household
        ).order_by('-id')
        return context


# ============================
# 投稿新規作成ビュー
# ============================
class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'posts/post_form.html'
    # 投稿完了後は掲示板一覧へ戻る
    success_url = reverse_lazy('posts:post_list')

    def form_valid(self, form):
        # 投稿者に自分をセットする
        form.instance.user = self.request.user

        # フォームから年・月・収支区分を取得する
        year = int(form.cleaned_data['year'])
        month = int(form.cleaned_data['month'])
        post_type = form.cleaned_data['post_type']
        # post_typeを文字列として保持する（'income' または 'expense'）
        tx_type_str = post_type
        tx_type = Transaction.INCOME if post_type == 'income' else Transaction.EXPENSE

        # 現在の家計簿を取得する
        household = get_current_household(self.request)

        # 家計簿名を保存する（入力がなければ現在の家計簿名を使う）
        household_name = form.cleaned_data.get('household_name', '').strip()
        if not household_name:
            form.instance.household_name = household.name if household else ''
        else:
            form.instance.household_name = household_name

        # 指定年月の現在の家計簿の収支データを取得する
        qs = Transaction.objects.filter(
            household_account=household,
            date__year=year,
            date__month=month,
            tx_type=tx_type
        ).select_related('category')

        # カテゴリーごとに合計金額と色を計算する
        category_totals = {}
        category_colors = {}
        total_sum = 0

        for item in qs:
            if item.category:
                cat_name = item.category.name
                cat_color = item.category.color
            else:
                cat_name = '未分類'
                cat_color = '#95a5a6'
            if item.amount:
                category_totals[cat_name] = category_totals.get(cat_name, 0) + item.amount
                category_colors[cat_name] = cat_color
                total_sum += item.amount

        # カテゴリーの順番をorderフィールドの順番に揃える
        ordered_categories = Category.objects.filter(
            household_account=household,
            category_type=tx_type_str
        ).order_by('order').values_list('name', flat=True)

        # 順番通りに並び替えた辞書を作成する
        ordered_totals = {}
        ordered_colors = {}
        for cat_name in ordered_categories:
            if cat_name in category_totals:
                ordered_totals[cat_name] = category_totals[cat_name]
                ordered_colors[cat_name] = category_colors[cat_name]
        # 未分類は最後に追加する
        if '未分類' in category_totals:
            ordered_totals['未分類'] = category_totals['未分類']
            ordered_colors['未分類'] = '#95a5a6'

        # 集計結果をモデルに保存する
        form.instance.total_amount = total_sum
        form.instance.category_data = ordered_totals
        form.instance.category_colors = ordered_colors
        # 現在の家計簿を投稿に紐づける
        form.instance.household = household

        return super().form_valid(form)


# ============================
# いいねビュー
# ============================
class PostLikeView(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        post = Post.objects.get(pk=pk)
        # すでにいいねしている場合は取り消す、していない場合は追加する
        if request.user in post.likes.all():
            post.likes.remove(request.user)
            liked = False
        else:
            post.likes.add(request.user)
            liked = True
        return JsonResponse({
            'liked': liked,
            'count': post.number_of_likes()
        })


# ============================
# 投稿削除ビュー
# ============================
class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    # 削除後は掲示板一覧へ戻る
    success_url = reverse_lazy('posts:post_list')

    def get_queryset(self):
        # 自分の投稿だけを削除対象にする
        return Post.objects.filter(user=self.request.user)

    def get(self, request, *args, **kwargs):
        # GETリクエストでも即削除する（確認画面なし）
        return self.delete(request, *args, **kwargs)
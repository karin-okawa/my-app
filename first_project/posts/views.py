# 画面を表示するためのショートカット機能をインポート
from django.shortcuts import render

# 一覧画面（リスト）を簡単に作るための機能をインポート
from django.views.generic import ListView

# ログインしていない人がページを開けないように制限する機能をインポート
from django.contrib.auth.mixins import LoginRequiredMixin

# 掲示板のデータを保存する「Post」モデルを読み込み
from .models import Post

# 新規作成画面（フォーム）を簡単に作るための機能をインポート
from django.views.generic import CreateView

# 処理が終わった後に別のページへ移動（リダイレクト）させるための機能をインポート
from django.urls import reverse_lazy

# 掲示板投稿用の入力フォーム設定を読み込み
from .forms import PostForm

# 家計簿アプリ側の収支データ（Transaction）を参照するためにインポート
from households.models import Transaction

# データベース内の数値を合計（足し算）するための機能をインポート
from django.db.models import Sum


from .forms import PostForm

from django.views.generic import DeleteView
from django.http import JsonResponse
from django.views import View




# --- 掲示板の一覧（みんなの投稿・わたしの投稿）を表示するクラス ---
class PostListView(LoginRequiredMixin, ListView):
    # どのデータを表示対象にするか（掲示板のPostモデル）
    model = Post
    template_name = 'posts/post_list.html'
    context_object_name = 'all_posts'

    # HTMLに渡すデータ（ context ）を準備するメソッド
    def get_context_data(self, **kwargs):
        # まずは親クラスが持っている標準的なデータ（全件リストなど）を取得
        context = super().get_context_data(**kwargs)
        
        # モーダル内の入力項目（年・月など）を表示するための空フォームを渡す
        context['form'] = PostForm() 
        
        # 「わたしの投稿」タブに表示するため、ログイン中ユーザーの投稿だけを最新順で取得
        context['my_posts'] = Post.objects.filter(user=self.request.user).order_by('-id')
        
        # 準備したすべてのデータをHTMLに送る
        return context
    

# --- 家計簿レポートを新しく投稿するためのクラス ---
class PostCreateView(LoginRequiredMixin, CreateView):
    # どのモデルにデータを保存するか
    model = Post
    # どのフォームを使って入力を受け付けるか
    form_class = PostForm
    # 入力画面に使用するHTMLファイルを指定
    template_name = 'posts/post_form.html'
    # 投稿が無事に完了した後に自動で移動する先（掲示板の一覧画面）を指定
    success_url = reverse_lazy('posts:post_list')

    # 入力された内容を保存する直前に実行される処理
    def form_valid(self, form):
        # 投稿者に自分をセット
        form.instance.user = self.request.user
        
        # フォームから年・月・区分を取得
        year = int(form.cleaned_data['year'])
        month = int(form.cleaned_data['month'])
        post_type = form.cleaned_data['post_type']
        tx_type = Transaction.INCOME if post_type == 'income' else Transaction.EXPENSE
        
        # 現在の家計簿を取得する
        from home.views import get_current_household
        household = get_current_household(self.request)
        
        # 指定年月の現在の家計簿のデータを取得する
        qs = Transaction.objects.filter(
            household_account=household,
            date__year=year,
            date__month=month,
            tx_type=tx_type
        ).select_related('category')
        
        # カテゴリごとに合計金額と色を計算する
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
        
        form.instance.total_amount = total_sum
        form.instance.category_data = category_totals
        # カテゴリーの色情報も保存する
        form.instance.category_colors = category_colors
        
        return super().form_valid(form)
        

# いいね機能
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

# 投稿削除
class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    success_url = reverse_lazy('posts:post_list')

    def get_queryset(self):
        # 自分の投稿だけを削除対象にする
        return Post.objects.filter(user=self.request.user)

    def get(self, request, *args, **kwargs):
        # GETリクエストでも即削除する
        return self.delete(request, *args, **kwargs)
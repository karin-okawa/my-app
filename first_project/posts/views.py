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
        
        # --- カテゴリごとの内訳を集計 ---
        # 指定年月の自分のデータを取得
        qs = Transaction.objects.filter(
            user=self.request.user,
            date__year=year,
            date__month=month,
            tx_type=tx_type
        )
        
        # カテゴリごとに合計金額を計算して辞書形式にする
        # 例: {'食費': 30000, '日用品': 5000}
        category_totals = {}
        total_sum = 0
        
        for item in qs:
            cat_name = item.category.name # カテゴリ名を取得
            amount = item.amount
            category_totals[cat_name] = category_totals.get(cat_name, 0) + amount
            total_sum += amount
        
        # モデルに保存
        form.instance.total_amount = total_sum
        form.instance.category_data = category_totals # これがグラフの元データになります
        
        return super().form_valid(form)
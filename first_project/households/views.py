# ログインしていない人をログイン画面に飛ばすためのMixin
from django.contrib.auth.mixins import LoginRequiredMixin
# 一覧表示・新規作成・更新・削除用の汎用CBV
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
# URL名からURLを作るための関数
from django.urls import reverse_lazy
# forms.py のフォームを使う
from .forms import TransactionForm
# JSONレスポンスを返すために使う
from django.http import JsonResponse
# 日付を扱うために使う
from datetime import date
# Viewの基本クラス（LoginRequiredMixinと組み合わせてログイン必須にする）
from django.views import View
# JSON形式でレスポンスを返すためのクラス
from django.http import JsonResponse
# フロントから送られてくるJSON文字列をPythonのデータに変換するための標準ライブラリ
import json
# ランダムな色を選ぶために使う標準ライブラリ
import random
# households/models.py のTransaction・Category・CustomColorモデルを使う
from .models import Transaction, Category, CustomColor

from home.views import get_current_household

# ============================
# 収支一覧ページ
# ============================
class TransactionListView(LoginRequiredMixin, ListView):
    # ログインユーザーの収支データだけを一覧表示する
    model = Transaction
    # 使用するテンプレート
    template_name = "households/transaction_list.html"
    # テンプレートで使う変数名
    context_object_name = "transactions"

    def get_queryset(self):
        # 自分のデータだけに絞り込む
        return Transaction.objects.filter(user=self.request.user)


# ============================
# 収支登録ページ
# ============================
class TransactionCreateView(LoginRequiredMixin, CreateView):
    # 収支登録画面
    model = Transaction
    # forms.pyの設定を使う
    form_class = TransactionForm
    # 使用するテンプレート
    template_name = "households/transaction_form.html"
    # 登録成功後 → 収支一覧へ戻る
    success_url = reverse_lazy("households:list")

    def form_valid(self, form):
        # 保存前にログインユーザーを自動設定
        form.instance.user = self.request.user
        return super().form_valid(form)


# ============================
# 収支編集ページ
# ============================
class TransactionUpdateView(LoginRequiredMixin, UpdateView):
    # 収支編集画面
    model = Transaction
    # forms.pyの設定を使う
    form_class = TransactionForm
    # 使用するテンプレート
    template_name = "households/transaction_form.html"
    # 編集成功後 → 収支一覧へ戻る
    success_url = reverse_lazy("households:list")

    def get_queryset(self):
        # 自分のデータだけを編集対象にする
        return Transaction.objects.filter(user=self.request.user)


# ============================
# 指定日付の収支データをJSONで返すAPI
# ============================
class DayTransactionsJsonView(LoginRequiredMixin, ListView):
    model = Transaction

    def get(self, request, *args, **kwargs):
        # URLから年月日を取得
        y = int(kwargs["year"])
        m = int(kwargs["month"])
        d = int(kwargs["day"])
        target = date(y, m, d)

        # 指定日付の自分のデータを取得
        qs = Transaction.objects.filter(
            user=request.user,
            date=target
        ).order_by("-created_at")

        # JSONに変換するデータを作成
        data = []
        for tx in qs:
            data.append({
                "id": tx.id,
                "tx_type": tx.tx_type,
                "tx_type_label": tx.get_tx_type_display(),
                "amount": tx.amount,
                "memo": tx.memo or "",
                "label": tx.memo or tx.get_tx_type_display(),
            })

        return JsonResponse({
            "date": target.isoformat(),
            "transactions": data,
        })


# ============================
# カテゴリー一覧ページ
# ============================
class CategoryListView(LoginRequiredMixin, ListView):
    # カテゴリーを一覧表示する
    model = Category
    # 使用するテンプレート
    template_name = "households/category_list.html"
    # テンプレートで使う変数名
    context_object_name = "categories"
    
    def get_queryset(self):
        # 現在の家計簿に紐づいたカテゴリーだけを表示する
        household = get_current_household(self.request)
        category_type = self.request.GET.get('type')
        qs = Category.objects.filter(household_account=household)
        if category_type in ['income', 'expense']:
            qs = qs.filter(category_type=category_type)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # テンプレートでも収支タイプを使えるようにする
        context['category_type'] = self.request.GET.get('type', '')
        return context


# ============================
# カテゴリー編集ページ
# ============================
class CategoryUpdateView(LoginRequiredMixin, UpdateView):
    # カテゴリーを編集する
    model = Category
    # 編集できる項目：カテゴリー名・種類・色
    fields = ['name', 'category_type', 'color']
    # 使用するテンプレート
    template_name = "households/category_form.html"
    
    def get_success_url(self):
        # 編集成功後は収支タイプを引き継いでカテゴリー一覧へ戻る
        category_type = self.request.GET.get('type', '')
        return f"{reverse_lazy('households:category_list')}?type={category_type}"


# ============================
# カテゴリー削除ページ
# ============================
class CategoryDeleteView(LoginRequiredMixin, DeleteView):
    # カテゴリーを削除する
    model = Category
    # 使用するテンプレート
    template_name = "households/category_confirm_delete.html"
    # 削除成功後 → カテゴリー一覧へ戻る
    success_url = reverse_lazy('households:category_list')
    

class CategoryReorderView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        try:
            # フロントから送られてくる順番データをJSONで受け取る
            data = json.loads(request.body)
            order_list = data.get('order', [])
            
            # 受け取った順番通りにorderフィールドを更新する
            for index, category_id in enumerate(order_list):
                Category.objects.filter(id=category_id).update(order=index)
            
            return JsonResponse({'status': 'ok'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

        
# カテゴリーの色選択ページ
class CategoryColorView(LoginRequiredMixin, UpdateView):
    # Categoryモデルのcolorフィールドだけを更新する
    model = Category
    fields = ['color']
    template_name = "households/category_color.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 現在編集中のカテゴリーの収支タイプを取得する
        category_type = self.object.category_type
        # 同じ収支タイプのカテゴリーで使われている色を重複なしで取得する
        used_colors = list(
            Category.objects.filter(category_type=category_type)
            .values_list('color', flat=True)
            .distinct()
        )
        context['used_colors'] = used_colors
        # プリセットカラーの一覧をテンプレートに渡す
        context['preset_colors'] = [
          '#e74c3c', '#e67e22', '#f1c40f', '#2ecc71',
          '#3498db', '#9c6d5c', '#2c3e50', '#95a5a6', '#9b59b6'
        ]
        # 同じ収支タイプのカスタムカラーを取得する
        context['custom_colors'] = list(
            CustomColor.objects.filter(category_type=category_type)
            .values_list('color', flat=True)
        )
        return context
    
    def form_valid(self, form):
        # 選択した色がプリセットカラーに含まれていない場合はカスタムカラーとして保存する
        preset_colors = [
          '#e74c3c', '#e67e22', '#f1c40f', '#2ecc71',
          '#3498db', '#9c6d5c', '#2c3e50', '#95a5a6', '#9b59b6'
        ]
        selected_color = form.instance.color
        if selected_color not in preset_colors:
            # カスタムカラーをDBに保存する（すでに存在する場合は保存しない）
            CustomColor.objects.get_or_create(
                category_type=self.object.category_type,
                color=selected_color
            )
        return super().form_valid(form)
    
    def get_success_url(self):
        category_type = self.request.GET.get('type', '')
        from_page = self.request.GET.get('from', '')
        if from_page == 'create':
            # 新規作成からの場合はカテゴリー一覧へ戻る
            return f"{reverse_lazy('households:category_list')}?type={category_type}"
        # 編集からの場合はカテゴリー編集画面へ戻る
        return f"{reverse_lazy('households:category_edit', kwargs={'pk': self.object.pk})}?type={category_type}"


# カテゴリー追加のページ
class CategoryCreateView(LoginRequiredMixin, CreateView):
    # カテゴリーを新規作成する
    model = Category
    # 入力項目：カテゴリー名・種類・色
    fields = ['name', 'category_type', 'color']
    # 使用するテンプレート
    template_name = "households/category_form.html"
    

    def get_initial(self):
        initial = super().get_initial()
        # プリセットカラーの中からランダムで1色を初期値に設定する
        preset_colors = [
            '#e74c3c', '#e67e22', '#f1c40f', '#2ecc71',
            '#3498db', '#9c6d5c', '#2c3e50', '#95a5a6', '#9b59b6'
        ]
        initial['color'] = random.choice(preset_colors)
        # URLパラメータからcategory_typeを取得して初期値に設定する
        category_type = self.request.GET.get('type')
        if category_type in ['income', 'expense']:
            initial['category_type'] = category_type
        return initial
        
    def form_valid(self, form):
        # 常にランダムで色を設定する（新規作成時は毎回ランダム）    
        preset_colors = [
            '#e74c3c', '#e67e22', '#f1c40f', '#2ecc71',
            '#3498db', '#9c6d5c', '#2c3e50', '#95a5a6', '#9b59b6'
        ]
        form.instance.color = random.choice(preset_colors)

        # 現在の家計簿と紐づける
        household = get_current_household(self.request)
        form.instance.household_account = household

        # 同じhousehold_accountとcategory_typeの中で一番大きいorderの次の番号を設定する
        max_order = Category.objects.filter(
            household_account=household,
            category_type=form.instance.category_type
        ).order_by('-order').values_list('order', flat=True).first()
        form.instance.order = (max_order or 0) + 1

        return super().form_valid(form)  

    def get_success_url(self):
    # 作成成功後はすぐに色選択画面へ遷移する
        category_type = self.request.GET.get('type', '')
        return f"{reverse_lazy('households:category_color', kwargs={'pk': self.object.pk})}?type={category_type}&from=create"
# ①Django標準機能
from django.contrib.auth.mixins import LoginRequiredMixin  # ログイン必須Mixinのインポート
from django.views.generic import ListView, CreateView, UpdateView, DeleteView  # 汎用ビュークラスのインポート
from django.views import View  # Viewの基本クラスのインポート
from django.urls import reverse_lazy  # 名前付きURLパターンからURLを動的に生成する関数のインポート
from django.http import JsonResponse  # JSONレスポンス生成クラスのインポート
from django.db.models import Sum  # DB集計用（合計）関数のインポート

# ②その他のライブラリ
from datetime import date  # 日付を扱うクラスのインポート
import json  # フロントから送られてくるJSON文字列をPythonのデータに変換する標準ライブラリのインポート
import random  # ランダムな色を選ぶための標準ライブラリのインポート

# ③このアプリ内のモデルとフォーム
from .forms import TransactionForm  # このアプリ内のフォームクラスのインポート
from .models import Transaction, Category, CustomColor  # このアプリ内のモデルのインポート

# ④他アプリの関数
from home.views import get_current_household  # 現在選択中の家計簿を取得する関数のインポート


# ============================
# 収支一覧ビュー
# ============================
class TransactionListView(LoginRequiredMixin, ListView):
    model = Transaction
    # 使用するテンプレート
    template_name = "households/transaction_list.html"
    # テンプレートで使う変数名
    context_object_name = "transactions"

    def get_queryset(self):
        # 現在の家計簿に紐づいたデータだけに絞り込む
        return Transaction.objects.filter(user=self.request.user)


# ============================
# 収支登録ビュー
# ============================
class TransactionCreateView(LoginRequiredMixin, CreateView):
    model = Transaction
    form_class = TransactionForm
    template_name = "households/transaction_form.html"
    # 登録成功後は収支一覧へ戻る
    success_url = reverse_lazy("households:list")

    def form_valid(self, form):
        # 保存前にログインユーザーを自動設定する
        form.instance.user = self.request.user
        return super().form_valid(form)


# ============================
# 収支編集ビュー
# ============================
class TransactionUpdateView(LoginRequiredMixin, UpdateView):
    model = Transaction
    form_class = TransactionForm
    template_name = "households/transaction_form.html"
    # 編集成功後は収支一覧へ戻る
    success_url = reverse_lazy("households:list")

    def get_queryset(self):
        # 自分のデータだけを編集対象にする
        return Transaction.objects.filter(user=self.request.user)


# ============================
# 指定日付の収支データをJSON形式で返すビュー
# ============================
class DayTransactionsJsonView(LoginRequiredMixin, ListView):
    model = Transaction

    def get(self, request, *args, **kwargs):
        # URLから年月日を取得する
        y = int(kwargs["year"])
        m = int(kwargs["month"])
        d = int(kwargs["day"])
        target = date(y, m, d)

        # 指定日付の収支データを取得する
        qs = Transaction.objects.filter(
            user=request.user,
            date=target
        ).order_by("-created_at")

        # JSONに変換するデータを作成する
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
# カテゴリー一覧ビュー
# ============================
class CategoryListView(LoginRequiredMixin, ListView):
    model = Category
    template_name = "households/category_list.html"
    context_object_name = "categories"

    def get_queryset(self):
        # 現在の家計簿に紐づいたカテゴリーだけを表示する
        household = get_current_household(self.request)
        category_type = self.request.GET.get('type')
        qs = Category.objects.filter(household_account=household)
        # 収支タイプが指定されている場合はさらに絞り込む
        if category_type in ['income', 'expense']:
            qs = qs.filter(category_type=category_type)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # テンプレートでも収支タイプを使えるようにする
        context['category_type'] = self.request.GET.get('type', '')
        return context


# ============================
# カテゴリー編集ビュー
# ============================
class CategoryUpdateView(LoginRequiredMixin, UpdateView):
    model = Category
    # 編集できる項目：カテゴリー名・種類・色
    fields = ['name', 'category_type', 'color']
    template_name = "households/category_form.html"

    def get_success_url(self):
        # 編集成功後は収支タイプを引き継いでカテゴリー一覧へ戻る
        category_type = self.request.GET.get('type', '')
        return f"{reverse_lazy('households:category_list')}?type={category_type}"


# ============================
# カテゴリー削除ビュー
# ============================
class CategoryDeleteView(LoginRequiredMixin, DeleteView):
    model = Category
    template_name = "households/category_confirm_delete.html"

    def post(self, request, *args, **kwargs):
        # 削除前にcategory_typeをインスタンス変数として保存しておく
        obj = self.get_object()
        self.category_type = obj.category_type
        return super().post(request, *args, **kwargs)

    def get_success_url(self):
        # 削除したカテゴリーの収支タイプでリダイレクト先を決める
        return f"{reverse_lazy('households:category_list')}?type={self.category_type}"

    def get_queryset(self):
        # 現在の家計簿のカテゴリーだけを削除対象にする
        household = get_current_household(self.request)
        return Category.objects.filter(household_account=household)


# ============================
# カテゴリー並び替えビュー
# ============================
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


# ============================
# カテゴリー色選択ビュー
# ============================
class CategoryColorView(LoginRequiredMixin, UpdateView):
    # Categoryモデルのcolorフィールドだけを更新する
    model = Category
    fields = ['color']
    template_name = "households/category_color.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 現在編集中のカテゴリーの収支タイプを取得する
        category_type = self.object.category_type
        # 現在の家計簿の同じ収支タイプで使われている色を取得する
        household = get_current_household(self.request)
        used_colors = list(
            Category.objects.filter(
                category_type=category_type,
                household_account=household
            )
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


# ============================
# カテゴリー新規作成ビュー
# ============================
class CategoryCreateView(LoginRequiredMixin, CreateView):
    model = Category
    # 入力項目：カテゴリー名・種類・色
    fields = ['name', 'category_type', 'color']
    template_name = "households/category_form.html"

    def get_initial(self):
        initial = super().get_initial()
        # プリセットカラーの中からランダムで1色を初期値に設定する
        preset_colors = [
            '#e74c3c', '#e67e22', '#f1c40f', '#2ecc71',
            '#3498db', '#9c6d5c', '#2c3e50', '#95a5a6', '#9b59b6'
        ]
        initial['color'] = random.choice(preset_colors)
        # URLパラメーターからcategory_typeを取得して初期値に設定する
        category_type = self.request.GET.get('type')
        if category_type in ['income', 'expense']:
            initial['category_type'] = category_type
        return initial

    def form_valid(self, form):
        # 現在の家計簿と紐づける
        household = get_current_household(self.request)
        form.instance.household_account = household
        # 同じ家計簿・同じ収支タイプの中で最大のorderの次の番号を設定する
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
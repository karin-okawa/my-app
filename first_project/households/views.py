# ログインしていない人をログイン画面に飛ばすためのMixin
from django.contrib.auth.mixins import LoginRequiredMixin

# 一覧表示・新規作成用の汎用CBV
from django.views.generic import ListView, CreateView

# URL名からURLを作るための関数
from django.urls import reverse_lazy

# households/models.py の Transaction を使う
from .models import Transaction
from .forms import TransactionForm



class TransactionListView(LoginRequiredMixin, ListView):
    # 収支一覧画面・ログインユーザーのデータだけ表示する
  
    model = Transaction

    # 表示するテンプレート
    template_name = "households/transaction_list.html"

    # テンプレートで使う変数名
    context_object_name = "transactions"

    def get_queryset(self):
        
        # 表示するデータを「自分のものだけ」に制限
        return Transaction.objects.filter(user=self.request.user)


class TransactionCreateView(LoginRequiredMixin, CreateView):
    
    # 収支登録画面

    model = Transaction

    # forms.py の設定（labels など）を使うため、fields ではなく form_class を使う
    form_class = TransactionForm
    
    # 使用するテンプレート
    template_name = "households/transaction_form.html"

    # 登録成功後 → 収支一覧へ戻る
    success_url = reverse_lazy("households:list")

    def form_valid(self, form):
        # 保存前に「誰のデータか」をセット
        form.instance.user = self.request.user
        return super().form_valid(form)

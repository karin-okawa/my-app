# Djangoの「テンプレートを表示するだけ」のView（HTMLを返すため）
from django.views.generic import TemplateView

# ログインしていないユーザーをログイン画面へ飛ばすMixin
from django.contrib.auth.mixins import LoginRequiredMixin

# Python標準ライブラリのカレンダー機能
import calendar

# DB集計用（合計）
from django.db.models import Sum

# 日付（DateField）から「日（1〜31）」だけを取り出すための関数
from django.db.models.functions import ExtractDay

# households/models.py に定義してある Transaction モデルを使う
from households.models import Transaction


# --------------------------------------------
# ホーム画面（カレンダー＋日別収支を表示）
# --------------------------------------------
class HomeView(LoginRequiredMixin, TemplateView):
    """
    ログイン後に最初に表示されるホーム画面
    ・月カレンダーを表示する
    ・その月の「日別 収入 / 支出 合計」をテンプレに渡す
    """
    # 表示に使うテンプレート
    template_name = "home/home.html"

    def get_context_data(self, **kwargs):
        """
        テンプレートに渡すデータ（context）を作るメソッド
        """
        # まずは親クラス（TemplateView）が用意した context を取得
        context = super().get_context_data(**kwargs)

        # ============================
        # 表示する年月（まずは固定）
        # ============================
        year = 2026
        month = 2

        # ============================
        # カレンダーの枠を作る
        # ============================
        # firstweekday=6 → 日曜始まり
        # 戻り値は「週 × 曜日」の2次元リスト
        # 例：[[1,2,3,4,5,6,7], [8,9,10,11,12,13,14], ...]
        # 月に含まれない日は 0 になる
        cal = calendar.Calendar(firstweekday=6).monthdayscalendar(year, month)

        # テンプレートで {{ year }}, {{ month }}, {% for week in calendar %} が使えるようにする
        context["year"] = year
        context["month"] = month
        context["calendar"] = cal

        # ============================
        # この月の収支データを取得
        # ============================
        # ・ログインユーザーのものだけ
        # ・指定した年・月のものだけ
        qs = Transaction.objects.filter(
            user=self.request.user,
            date__year=year,
            date__month=month,
        )

        # ============================
        # 日別「収入合計」を作る
        # ============================
        # 1. tx_type が income のものだけに絞る
        # 2. date から「日」だけを取り出す（ExtractDay）
        # 3. 同じ日の amount を合計（Sum）
        income_by_day = (
            qs.filter(tx_type=Transaction.INCOME)
              .annotate(day=ExtractDay("date"))   # day = 1〜31
              .values("day")
              .annotate(total=Sum("amount"))      # total = その日の収入合計
        )

        # ============================
        # 日別「支出合計」を作る
        # ============================
        expense_by_day = (
            qs.filter(tx_type=Transaction.EXPENSE)
              .annotate(day=ExtractDay("date"))
              .values("day")
              .annotate(total=Sum("amount"))
        )

        # ============================
        # テンプレで使いやすい形に変換
        # ============================
        # QuerySet → 辞書に変換
        # 例：{ 2: 3000, 5: 1200 }
        context["income_map"] = {
            row["day"]: row["total"] for row in income_by_day
        }

        context["expense_map"] = {
            row["day"]: row["total"] for row in expense_by_day
        }

        # 最終的にこの context がテンプレートに渡される
        return context

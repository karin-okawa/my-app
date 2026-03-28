from django.conf import settings
from django.db import models

# --- カテゴリモデル ---
class Category(models.Model):
    # カテゴリ名（食費、日用品、給与など）
    name = models.CharField(max_length=50)

    # 収入用か支出用か（TransactionのTYPE_CHOICESと合わせる）
    # これにより「支出登録時は支出用カテゴリだけ出す」などの制御ができる
    category_type = models.CharField(
        max_length=10,
        choices=[("income", "収入"), ("expense", "支出")],
        default="expense"
    )

    # グラフやカテゴリー表示に使う色（HEXコードで保存 例：#FF0000）
    # デフォルトはアプリのテーマカラー（茶色）
    color = models.CharField(max_length=7, default="#9c6d5c")

    class Meta:
        verbose_name_plural = "Categories"  # 管理画面で末尾にsが重なるのを防ぐ

    def __str__(self):
        # 管理画面などで「食費（支出）」のように表示されるようにする
        type_label = "収入" if self.category_type == "income" else "支出"
        return f"{self.name}（{type_label}）"


# 家計簿の「1件の収支」を表すモデル
class Transaction(models.Model):
    INCOME = "income"
    EXPENSE = "expense"
    TYPE_CHOICES = [
        (INCOME, "収入"),
        (EXPENSE, "支出"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateField()
    tx_type = models.CharField(max_length=10, choices=TYPE_CHOICES)

    # --- カテゴリとの紐付けを追加 ---
    # null=True, blank=True にして、移行時や未設定時でもエラーにならないようにする
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,  # カテゴリが削除されても、収支データ自体は消さずに「未分類」にする
        null=True,
        blank=True,
        verbose_name="カテゴリ"
    )

    amount = models.PositiveIntegerField()
    memo = models.CharField(max_length=200, blank=True)
    image = models.ImageField(upload_to="receipts/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-created_at"]

    def __str__(self):
        # 表示にカテゴリ名を含める
        cat_name = self.category.name if self.category else "未分類"
        return f"{self.user} | {self.date} | {cat_name} | {self.amount}"

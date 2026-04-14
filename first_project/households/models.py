from django.conf import settings  # プロジェクト設定のインポート（AUTH_USER_MODELの参照に使用）
from django.db import models  # Djangoのモデルモジュールのインポート


# 家計簿モデル
class HouseholdAccount(models.Model):
    # 家計簿名（例：「自分用」「家族用」）
    name = models.CharField(max_length=25)
    # レコードの作成日時
    created_at = models.DateTimeField(auto_now_add=True)
    # レコードの最終更新日時
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


# 家計簿とユーザーの中間テーブル
class UserHouseholdAccount(models.Model):
    # 紐づくユーザー
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    # 紐づく家計簿
    household_account = models.ForeignKey(
        HouseholdAccount,
        on_delete=models.CASCADE
    )
    # 招待トークンのハッシュ
    invitation_token_hash = models.CharField(max_length=100, blank=True, null=True)
    # 招待リンクの有効期限
    expires_at = models.DateTimeField(blank=True, null=True)
    # 参加ステータス（0:未承認 1:承認済み 2:招待中）
    status = models.IntegerField(default=1)
    # ユーザーが家計簿に参加した日時
    joined_at = models.DateTimeField(blank=True, null=True)
    # レコードの作成日時
    created_at = models.DateTimeField(auto_now_add=True)
    # レコードの最終更新日時
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} - {self.household_account}"


# カテゴリーモデル
class Category(models.Model):
    # どの家計簿のカテゴリーか
    household_account = models.ForeignKey(
        HouseholdAccount,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    # カテゴリー名
    name = models.CharField(max_length=50)
    # カテゴリーの種別（収入 or 支出）
    category_type = models.CharField(
        max_length=10,
        choices=[("income", "収入"), ("expense", "支出")],
        default="expense"
    )
    # カテゴリーの表示色（16進数カラーコード）
    color = models.CharField(max_length=7, default="#9c6d5c")
    # カテゴリーの表示順
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name_plural = "Categories"
        # 表示順、次にIDで並び替え
        ordering = ['order', 'id']

    def __str__(self):
        type_label = "収入" if self.category_type == "income" else "支出"
        return f"{self.name}（{type_label}）"


# 収支モデル
class Transaction(models.Model):
    # 収支種別の定数
    INCOME = "income"
    EXPENSE = "expense"
    TYPE_CHOICES = [
        (INCOME, "収入"),
        (EXPENSE, "支出"),
    ]
    # 紐づく家計簿
    household_account = models.ForeignKey(
        HouseholdAccount,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    # 登録したユーザー（誰が登録したか追跡するため）
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    # 収支の日付
    date = models.DateField()
    # 収支種別（収入 or 支出）
    tx_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    # 紐づくカテゴリー（削除時はNULLにする）
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="カテゴリー"
    )
    # 金額
    amount = models.PositiveIntegerField(null=True, blank=True)
    # メモ
    memo = models.CharField(max_length=200, blank=True)
    # レシートなどの画像
    image = models.ImageField(upload_to="receipts/", blank=True, null=True)
    # レコードの作成日時
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # 日付の新しい順、次に作成日時の新しい順で並び替え
        ordering = ["-date", "-created_at"]

    def __str__(self):
        cat_name = self.category.name if self.category else "未分類"
        return f"{self.user} | {self.date} | {cat_name} | {self.amount}"


# カスタムカラーモデル
class CustomColor(models.Model):
    # カラーの種別（収入 or 支出）
    category_type = models.CharField(
        max_length=10,
        choices=[("income", "収入"), ("expense", "支出")],
        default="expense"
    )
    # 16進数カラーコード
    color = models.CharField(max_length=7)

    class Meta:
        # 同じ種別・同じ色の組み合わせは重複不可
        unique_together = ['category_type', 'color']

    def __str__(self):
        return f"{self.category_type} - {self.color}"
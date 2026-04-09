from django.conf import settings
from django.db import models

# 家計簿モデル
class HouseholdAccount(models.Model):
    # 家計簿名（例：「自分用」「家族用」）
    name = models.CharField(max_length=25)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


# 家計簿とユーザーの中間テーブル
class UserHouseholdAccount(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    household_account = models.ForeignKey(
        HouseholdAccount,
        on_delete=models.CASCADE
    )
    # 招待トークンのハッシュ
    invitation_token_hash = models.CharField(max_length=100, blank=True, null=True)
    # 招待リンクの有効期限
    expires_at = models.DateTimeField(blank=True, null=True)
    # 0:未承認 1:承認済み 2:招待中
    status = models.IntegerField(default=1)
    # ユーザーが家計簿に参加した日時
    joined_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} - {self.household_account}"


# カテゴリモデル
class Category(models.Model):
    # どの家計簿のカテゴリか
    household_account = models.ForeignKey(
        HouseholdAccount,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    name = models.CharField(max_length=50)
    category_type = models.CharField(
        max_length=10,
        choices=[("income", "収入"), ("expense", "支出")],
        default="expense"
    )
    color = models.CharField(max_length=7, default="#9c6d5c")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['order', 'id']

    def __str__(self):
        type_label = "収入" if self.category_type == "income" else "支出"
        return f"{self.name}（{type_label}）"


# 収支モデル
class Transaction(models.Model):
    INCOME = "income"
    EXPENSE = "expense"
    TYPE_CHOICES = [
        (INCOME, "収入"),
        (EXPENSE, "支出"),
    ]
    # userの代わりにhousehold_accountと紐づける
    household_account = models.ForeignKey(
        HouseholdAccount,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    # userも残しておく（誰が登録したか追跡するため）
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    date = models.DateField()
    tx_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="カテゴリ"
    )
    amount = models.PositiveIntegerField(null=True, blank=True)
    memo = models.CharField(max_length=200, blank=True)
    image = models.ImageField(upload_to="receipts/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-created_at"]

    def __str__(self):
        cat_name = self.category.name if self.category else "未分類"
        return f"{self.user} | {self.date} | {cat_name} | {self.amount}"


# カスタムカラーモデル
class CustomColor(models.Model):
    category_type = models.CharField(
        max_length=10,
        choices=[("income", "収入"), ("expense", "支出")],
        default="expense"
    )
    color = models.CharField(max_length=7)

    class Meta:
        unique_together = ['category_type', 'color']

    def __str__(self):
        return f"{self.category_type} - {self.color}"
from django.conf import settings
from django.db import models



# 家計簿の「1件の収支（収入 or 支出）」を表すモデル
# カレンダー表示・一覧表示・集計（合計など）の元になるデータをここに保存する
class Transaction(models.Model):

    # 収支の種類（収入/支出）を定数として定義
    # 文字列を直書きするとミスしやすいので、定数にして安全にする
    INCOME = "income"
    EXPENSE = "expense"

    # フォームや管理画面で「収入」「支出」と表示するための選択肢
    # DBには "income" / "expense" が保存される（表示は日本語）
    TYPE_CHOICES = [
        (INCOME, "収入"),
        (EXPENSE, "支出"),
    ]

    # ログインしているユーザー
    # settings.AUTH_USER_MODEL を使うことで、カスタムユーザーモデルでも安全に紐づけられる
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    # 収支を登録した日付（カレンダーに表示するときのキーになる）
    date = models.DateField()

    # 収入か支出か（選択式）
    # choices を指定すると、フォームが選択肢になり、DBには定義した値だけが入るようになる
    tx_type = models.CharField(
        max_length=10,
        choices=TYPE_CHOICES
    )

    # 金額（A案：金額は必須）
    # マイナスは使わない想定なので PositiveIntegerField にしている
    amount = models.PositiveIntegerField()

    # メモ（任意入力）
    # blank=True にするとフォームで未入力OKになる（DBは空文字で保存される）
    memo = models.CharField(
        max_length=200,
        blank=True
    )

    # レシートなどの画像（任意入力）
    # blank=True：フォームで未入力OK
    # null=True：DBにNULLを保存できる（未登録状態を表現できる）
    image = models.ImageField(
        upload_to="receipts/",
        blank=True,
        null=True
    )

    # 作成日時（自動で現在時刻が入る）
    # いつ登録されたかを後で追えるようにする
    created_at = models.DateTimeField(
        auto_now_add=True
    )

    # モデル全体に関する設定（並び順など）をまとめて書く場所
    class Meta:
        # 一覧表示するときのデフォルト並び順（新しい日付・新しい登録が上に来る）
        ordering = ["-date", "-created_at"]

    # 管理画面やデバッグで見やすくするための文字列表現
    def __str__(self):
        # user は表示名が設定されていればそれが出る（なければメールなど）
        return f"{self.user} | {self.date} | {self.tx_type} | {self.amount}"
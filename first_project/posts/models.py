from django.conf import settings  # プロジェクト設定のインポート（AUTH_USER_MODELの参照に使用）
from django.db import models  # Djangoのモデルモジュールのインポート
from households.models import HouseholdAccount  # 家計簿モデルのインポート


class Post(models.Model):
    """
    家計簿レポート投稿モデル
    """
    # 収支種別の選択肢
    TYPE_CHOICES = [('income', '収入'), ('expense', '支出')]

    # 投稿したユーザー
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    # 投稿内容
    year = models.IntegerField(verbose_name="対象年")
    month = models.IntegerField(verbose_name="対象月")
    post_type = models.CharField(max_length=10, choices=TYPE_CHOICES, verbose_name="収支区分")
    household_size = models.IntegerField(verbose_name="世帯人数")
    memo = models.TextField(max_length=500, blank=True, verbose_name="メモ")
    total_amount = models.IntegerField(default=0, verbose_name="合計金額")
    # カテゴリーごとの内訳を保存するフィールド（例：{"食費": 5000, "交際費": 2000}）
    category_data = models.JSONField(default=dict, verbose_name="カテゴリー別内訳")
    # カテゴリーの色情報を保存するフィールド
    category_colors = models.JSONField(default=dict, verbose_name="カテゴリー色情報")
    # 投稿時の家計簿名（公開用・変更可能）
    household_name = models.CharField(max_length=50, blank=True, verbose_name="家計簿名")
    # 紐づく家計簿（削除時はNULLにする）
    household = models.ForeignKey(
        HouseholdAccount,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="家計簿"
    )
    # いいね機能（誰がいいねしたかを記録）
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='liked_posts', blank=True)
    # レコードの作成日時
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # 作成日時の新しい順で並び替え
        ordering = ['-created_at']

    # いいね数を返すメソッド
    def number_of_likes(self):
        return self.likes.count()

    def __str__(self):
        return f"{self.user.username} - {self.year}/{self.month}"
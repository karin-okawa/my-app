from django.conf import settings
from django.db import models

class Post(models.Model):
    """
    家計簿レポート投稿モデル
    """
    TYPE_CHOICES = [('income', '収入'), ('expense', '支出')]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    # 投稿内容
    year = models.IntegerField(verbose_name="対象年")
    month = models.IntegerField(verbose_name="対象月")
    post_type = models.CharField(max_length=10, choices=TYPE_CHOICES, verbose_name="収支区分")
    household_size = models.IntegerField(verbose_name="世帯人数")
    memo = models.TextField(max_length=500, blank=True, verbose_name="メモ")
    total_amount = models.IntegerField(default=0, verbose_name="合計金額")
    
    # カテゴリごとの内訳を保存するフィールド（例：{"食費": 5000, "交際費": 2000}）
    category_data = models.JSONField(default=dict, verbose_name="カテゴリ別内訳")
    
    # カテゴリーの色情報を保存するフィールド
    category_colors = models.JSONField(default=dict, verbose_name="カテゴリー色情報")
    
    # いいね機能（誰がいいねしたかを記録）
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='liked_posts', blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def number_of_likes(self):
        return self.likes.count()

    def __str__(self):
        return f"{self.user.username} - {self.year}/{self.month}"
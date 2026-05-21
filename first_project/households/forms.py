from django import forms  # Djangoのフォームモジュールのインポート
from .models import Transaction, Category  # このアプリ内のモデルのインポート
from django.utils import timezone  # タイムゾーン対応の日時取得モジュールのインポート


class TransactionForm(forms.ModelForm):
    class Meta:
        # 使用するモデルの指定
        model = Transaction
        # フォームに表示するフィールド
        fields = ["date", "tx_type", "category", "amount", "memo", "image"]
        # ラベルの設定
        labels = {
            "date": "日付",
            "tx_type": "収支区分",
            "category": "カテゴリー",
            "amount": "金額",
            "memo": "メモ",
            "image": "画像",
        }
        # 見た目を整えるためのウィジェット設定
        widgets = {
            # 日付：カレンダーから選びやすくする
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            # カテゴリー：プルダウン（セレクトボックス）
            'category': forms.Select(attrs={'class': 'form-select'}),
            # 金額：数値入力
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'required': False}),
            # メモ：複数行テキスト入力（折り返し対応）
            'memo': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            # 画像：ファイル選択
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        # 家計簿をキーワード引数から取り出す（ない場合はNone）
        household = kwargs.pop('household', None)
        super().__init__(*args, **kwargs)
        if household:
            # 現在の家計簿のカテゴリーだけに絞り込む
            self.fields['category'].queryset = Category.objects.filter(household_account=household)
        else:
            # 家計簿が渡されない場合は空にする
            self.fields['category'].queryset = Category.objects.none()
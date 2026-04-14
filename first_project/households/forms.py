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
            # メモ：テキスト入力
            'memo': forms.TextInput(attrs={'class': 'form-control'}),
            # 画像：ファイル選択
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 全カテゴリーを選択肢として表示する
        self.fields['category'].queryset = Category.objects.all()
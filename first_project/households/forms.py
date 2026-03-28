from django import forms
from .models import Transaction, Category   # Categoryをインポート
from django.utils import timezone

class TransactionForm(forms.ModelForm):

    class Meta:
        model = Transaction
        
        fields = ["date", "tx_type", "category", "amount", "memo", "image"]

        labels = {
            "date": "日付",
            "tx_type": "収支区分",
            "category": "カテゴリ", # ラベルを追加
            "amount": "金額",
            "memo": "メモ",
            "image": "画像",
        }

        # 見た目を整えるためのウィジェット設定
        widgets = {
            # 日付：カレンダーから選びやすくする
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            
            # カテゴリ：プルダウン（セレクトボックス）
            'category': forms.Select(attrs={'class': 'form-select'}),
            
            # 金額：数値入力
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            
            # メモ：テキスト入力
            'memo': forms.TextInput(attrs={'class': 'form-control'}),
            
            # 画像：ファイル選択
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.all()
        
 
        
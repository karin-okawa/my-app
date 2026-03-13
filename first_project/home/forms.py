from django import forms
from households.models import Transaction

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        # ユーザー(user)はViewで自動設定するため、入力項目からは外す
        fields = ['date', 'tx_type', 'amount', 'memo']
        
        # 入力しやすくするための設定（ウィジェット）
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'memo': forms.Textarea(attrs={'rows': 2}),
        }
        labels = {
            'date': '日付',
            'tx_type': '種類',
            'amount': '金額',
            'memo': 'メモ',
        }
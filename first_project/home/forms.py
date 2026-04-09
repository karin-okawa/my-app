from django import forms
from households.models import Transaction, Category
from django.utils import timezone

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        # categoryフィールドを含める
        fields = ['date', 'tx_type', 'category', 'amount', 'memo', 'image']
        widgets = {
            # 日付：カレンダーから選びやすくする
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            # カテゴリ：プルダウン（セレクトボックス）
            'category': forms.Select(attrs={'class': 'form-select'}),
            # 金額：数値入力（必須ではないのでrequired=False）
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'required': False}),
            # メモ：テキスト入力
            'memo': forms.TextInput(attrs={'class': 'form-control'}),
            # 画像：ファイル選択
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        # 現在の家計簿をkwargsから受け取る
        household = kwargs.pop('household', None)
        super().__init__(*args, **kwargs)
        self.fields['amount'].required = False
        # 家計簿が指定されている場合はその家計簿のカテゴリーだけを表示する
        if household:
            self.fields['category'].queryset = Category.objects.filter(
                household_account=household
            )
        else:
            self.fields['category'].queryset = Category.objects.all()
from django import forms  # Djangoのフォームモジュールのインポート
from households.models import Transaction, Category  # 家計簿アプリのモデルのインポート
from django.utils import timezone  # タイムゾーン対応の日時取得モジュールのインポート


class TransactionForm(forms.ModelForm):
    class Meta:
        # 使用するモデルの指定
        model = Transaction
        # フォームに表示するフィールド
        fields = ['date', 'tx_type', 'category', 'amount', 'memo', 'image']
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
        # 現在の家計簿をkwargsから受け取る
        household = kwargs.pop('household', None)
        super().__init__(*args, **kwargs)
        # 金額フィールドを任意入力にする
        self.fields['amount'].required = False
        # 家計簿が指定されている場合はその家計簿のカテゴリーだけを表示する
        if household:
            self.fields['category'].queryset = Category.objects.filter(
                household_account=household
            )
        else:
            self.fields['category'].queryset = Category.objects.all()
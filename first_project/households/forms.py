from django import forms
from .models import Transaction, Category  # Categoryをインポート
from django.utils import timezone

class TransactionForm(forms.ModelForm):

    class Meta:
        model = Transaction
        # 【修正】fieldsに "category" を追加
        fields = ["date", "tx_type", "category", "amount", "memo", "image"]

        labels = {
            "date": "日付",
            "tx_type": "収支区分",
            "category": "カテゴリ", # ラベルを追加
            "amount": "金額",
            "memo": "メモ",
            "image": "画像",
        }

        # 【修正】見た目を整えるためのウィジェット設定
        widgets = {
            # 日付：カレンダーから選びやすくする
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            
            # カテゴリ：プルダウン（セレクトボックス）
            'category': forms.Select(attrs={'class': 'form-select'}),
            
            # 金額：数値入力
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '金額を入力'}),
            
            # メモ：テキスト入力
            'memo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '例：スーパーでの買い物'}),
            
            # 画像：ファイル選択
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # 1. 収支区分の選択肢を固定
        self.fields['tx_type'].choices = [('income', '収入'), ('expense', '支出')]
        
        # 2. 初期値の設定
        if not self.instance.pk:
            self.fields['tx_type'].initial = 'expense'
            self.fields['date'].initial = timezone.now().date()

        self.fields['category'].empty_label = "カテゴリを選択"

        # --- 【ここから重要】カテゴリの動的フィルタリング ---
        # 編集時（instanceがある場合）は、その収支区分に合ったカテゴリだけを表示
        if self.instance and self.instance.pk:
            self.fields['category'].queryset = Category.objects.filter(
                category_type=self.instance.tx_type
            )
        else:
            # 新規作成時は、初期値の「支出(expense)」用カテゴリを表示
            self.fields['category'].queryset = Category.objects.filter(
                category_type='expense'
            )
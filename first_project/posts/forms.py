from django import forms
from .models import Post
from datetime import datetime

class PostForm(forms.ModelForm):
    # --- 選択肢の自動生成 ---

    # 世帯人数：1人〜10人のリストを生成
    HOUSEHOLD_CHOICES = [(i, f"{i}人暮らし") for i in range(1, 11)]
    
    # 年：今年から過去50年分を逆順で生成（例: 2026, 2025, 2024...）
    this_year = datetime.now().year
    YEAR_CHOICES = [(y, f"{y}年") for y in range(this_year, this_year - 51, -1)]
    
    # 月：1月〜12月のリストを生成
    MONTH_CHOICES = [(m, f"{m}月") for m in range(1, 13)]

    # 投稿タイプ：収入・支出の固定リスト
    POST_TYPE_CHOICES = [('income', '収入'), ('expense', '支出')]

    # --- 各フィールドの定義 ---

    # ChoiceField で定義し、initial（初期値）を指定することで「------」をなくす
    
    # 年のプルダウン設定
    year = forms.ChoiceField(
        choices=YEAR_CHOICES, 
        label="対象年", 
        widget=forms.Select(attrs={
            'class': 'form-select',
            'size': '6', # ここを 6 にすると、最初から6件分の高さで表示され、中でスクロールになります
        })
    )

    # 月のプルダウン設定
    month = forms.ChoiceField(
        choices=MONTH_CHOICES, 
        label="対象月", 
        widget=forms.Select(attrs={
            'class': 'form-select',
            'size': '6', # 年と同じく6件分に固定
        })
    )

    # initial を設定
    post_type = forms.ChoiceField(
        choices=POST_TYPE_CHOICES,
        label="投稿タイプ",
        initial='expense', # 最初から「支出」にチェックを入れる
        widget=forms.RadioSelect(attrs={'class': 'btn-check'})
    )

    household_size = forms.ChoiceField(
        choices=HOUSEHOLD_CHOICES, 
        label="世帯人数", 
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    class Meta:
        model = Post
        # 表示する順番通りに並べています
        fields = ['year', 'month', 'post_type', 'household_size', 'memo']
        widgets = {
            # メモ入力欄のデザイン設定
            'memo': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3, 
                'placeholder': '家計簿のポイントを教えてください'
            }),
        }
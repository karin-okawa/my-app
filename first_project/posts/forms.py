from django import forms  # Djangoのフォームモジュールのインポート
from .models import Post  # このアプリ内のモデルのインポート
from datetime import datetime  # 現在日時取得クラスのインポート


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
    # 年のプルダウン（最初から6件分の高さで表示し、中でスクロール）
    year = forms.ChoiceField(
        choices=YEAR_CHOICES,
        label="対象年",
        widget=forms.Select(attrs={
            'class': 'form-select',
            'size': '6',
        })
    )
    # 月のプルダウン（年と同じく6件分に固定）
    month = forms.ChoiceField(
        choices=MONTH_CHOICES,
        label="対象月",
        widget=forms.Select(attrs={
            'class': 'form-select',
            'size': '6',
        })
    )
    # 投稿タイプの選択（初期値は「支出」）
    post_type = forms.ChoiceField(
        choices=POST_TYPE_CHOICES,
        label="投稿タイプ",
        initial='expense',
        widget=forms.RadioSelect(attrs={'class': 'btn-check'})
    )
    # 世帯人数のプルダウン
    household_size = forms.ChoiceField(
        choices=HOUSEHOLD_CHOICES,
        label="世帯人数",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        # 使用するモデルの指定
        model = Post
        # フォームに表示するフィールド
        fields = ['year', 'month', 'post_type', 'household_size', 'household_name', 'memo']
        widgets = {
            # 家計簿名入力欄のデザイン設定
            'household_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '家計簿名',
                'style': 'border-radius: 10px; border: 1px solid #ddd; padding: 8px 12px; font-size: 0.9rem;',
            }),
            # メモ入力欄のデザイン設定
            'memo': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': '家計簿のポイントを教えてください'
            }),
        }
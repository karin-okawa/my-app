from django import forms
from .models import Transaction
# 現在の日付（今日）を取得するために必要
from django.utils import timezone

# Transaction（収支）を登録・編集するためのフォーム
# ModelForm を使うと「モデルの定義」からフォームの入力欄を自動で作ってくれるからコードを短く・安全に書ける
class TransactionForm(forms.ModelForm):

    # Meta クラスは「このフォームがどのモデルを元にしているか」や
    # 「フォームに出すフィールドはどれか」をまとめて指定する場所
    class Meta:
        # どのモデルのフォームか（Transaction を元にする）
        model = Transaction

        # フォームに表示して入力させたい項目だけを指定する
        # user はログイン中ユーザーを自動で紐づけたいので、フォームには出さない
        fields = ["date", "tx_type", "amount", "memo", "image"]

        # 入力欄の表示ラベルを日本語にしたい場合はここで指定できる
        labels = {
            "date": "日付",
            "tx_type": "収支区分",
            "amount": "金額",
            "memo": "メモ",
            "image": "画像",
         }
         # HTMLでカレンダーから選びやすくするための設定
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def clean_date(self):
        """
        日付項目のチェック。未来の日付ならエラーを出す
        """
        # 画面から入力された日付を取得
        input_date = self.cleaned_data.get('date')
        # システム上の「今日」の日付を取得
        today = timezone.now().date()

        # もし入力された日付が今日よりも後の日（未来）だった場合
        if input_date > today:
            # Djangoにエラーを伝え、画面にメッセージを出す
            raise forms.ValidationError("未来の日付は登録できません。")
        
        # チェックを通過した（今日以前だった）場合はそのままの値を返す
        return input_date

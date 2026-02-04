from django import forms
from .models import Transaction


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

       

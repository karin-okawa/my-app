from django.shortcuts import render  # 画面描画関数のインポート


# ポートフォリオのトップ画面ビュー
def index(request):
    return render(request, 'portfolio.html')
from django import template  # Djangoテンプレートモジュールのインポート

# カスタムテンプレートフィルターの登録
register = template.Library()

@register.filter
def dict_get(d, key):
    """
    テンプレートから辞書の値を取り出すためのカスタムフィルター
    使い方: {{ income_map|dict_get:day }}
    """
    if d is None:
        return None
    return d.get(key)
from django import template

register = template.Library()

@register.filter
def dict_get(d, key):
    """
    テンプレートから辞書の値を取り出すためのフィルター
    使い方: {{ income_map|dict_get:day }}
    """
    if d is None:
        return None
    return d.get(key)

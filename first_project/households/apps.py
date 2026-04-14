from django.apps import AppConfig  # AppConfigクラスのインポート

class HouseholdsConfig(AppConfig):
    # モデルの主キーに使用する自動採番フィールドの型
    default_auto_field = 'django.db.models.BigAutoField'
    # このアプリケーションの名前
    name = 'households'
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'first_project.settings')
django.setup()

from households.models import HouseholdAccount, Category

household = HouseholdAccount.objects.first()
default_categories = [
    {'name': '食費', 'category_type': 'expense', 'color': '#e74c3c', 'order': 1},
    {'name': '日用品費', 'category_type': 'expense', 'color': '#e67e22', 'order': 2},
    {'name': '衣服費', 'category_type': 'expense', 'color': '#f1c40f', 'order': 3},
    {'name': '交通費', 'category_type': 'expense', 'color': '#2ecc71', 'order': 4},
    {'name': '趣味費', 'category_type': 'expense', 'color': '#3498db', 'order': 5},
    {'name': '交際費', 'category_type': 'expense', 'color': '#9b59b6', 'order': 6},
    {'name': '固定費', 'category_type': 'expense', 'color': '#2c3e50', 'order': 7},
    {'name': 'その他', 'category_type': 'expense', 'color': '#95a5a6', 'order': 8},
    {'name': '給与', 'category_type': 'income', 'color': '#2ecc71', 'order': 1},
    {'name': 'その他', 'category_type': 'income', 'color': '#95a5a6', 'order': 2},
]

for cat in default_categories:
    Category.objects.create(household_account=household, **cat)

print("カテゴリー作成完了")
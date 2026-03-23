from django.db import migrations

def create_default_categories(apps, schema_editor):
    Category = apps.get_model('households', 'Category')
    
    # 支出用カテゴリ
    expense_cats = ["食費", "日用品", "住居費", "水道光熱費", "通信費", "交際費", "娯楽", "美容・衣服", "医療・保険", "その他"]
    for name in expense_cats:
        Category.objects.get_or_create(name=name, category_type="expense")
    
    # 収入用カテゴリ
    income_cats = ["給与", "ボーナス", "副業", "お小遣い", "その他"]
    for name in income_cats:
        Category.objects.get_or_create(name=name, category_type="income")

class Migration(migrations.Migration):
    dependencies = [
        ('households', '0002_category_transaction_category'), 
    ]

    operations = [
        migrations.RunPython(create_default_categories),
    ]
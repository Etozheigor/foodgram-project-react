# Generated by Django 2.2.19 on 2023-01-06 12:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0012_auto_20230106_1537'),
    ]

    operations = [
        migrations.RenameField(
            model_name='favorite',
            old_name='recipes',
            new_name='recipe',
        ),
        migrations.RenameField(
            model_name='shoppingcart',
            old_name='recipes',
            new_name='recipe',
        ),
    ]
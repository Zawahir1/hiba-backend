# Generated by Django 5.0.7 on 2025-02-28 19:11

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0002_blogscategories_blogs_category"),
    ]

    operations = [
        migrations.AddField(
            model_name="blogscategories",
            name="img",
            field=models.ImageField(blank=True, null=True, upload_to="categories/"),
        ),
    ]

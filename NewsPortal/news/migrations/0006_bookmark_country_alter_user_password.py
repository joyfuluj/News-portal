# Generated by Django 5.0.6 on 2024-07-04 23:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("news", "0005_alter_user_password"),
    ]

    operations = [
        migrations.AddField(
            model_name="bookmark",
            name="country",
            field=models.CharField(default=None, max_length=100),
        ),
        migrations.AlterField(
            model_name="user",
            name="password",
            field=models.CharField(
                default="pbkdf2_sha256$720000$pc183UqSIM7UjhR1lcBY15$fdA1yxuNZiMoNC5JBxHoZMqucDjgO4AdOmwpzTc9gEc=",
                max_length=128,
            ),
        ),
    ]

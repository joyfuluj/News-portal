# Generated by Django 5.0.6 on 2024-05-20 03:10

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='email',
            field=models.EmailField(default='default@default.com', max_length=254, unique=True),
        ),
        migrations.AddField(
            model_name='user',
            name='password',
            field=models.CharField(default='pbkdf2_sha256$720000$G724sdeSvNmTDCEsshbOkF$gGJmJZH1CjHsH9h6QCii2KW1Mv5JOMZCDJcxDGKIweQ=', max_length=128),
        ),
        migrations.AlterField(
            model_name='bookmark',
            name='content',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='bookmark',
            name='date_bookmarked',
            field=models.DateField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='bookmark',
            name='image_url',
            field=models.URLField(),
        ),
        migrations.AlterField(
            model_name='bookmark',
            name='url',
            field=models.URLField(),
        ),
        migrations.AlterField(
            model_name='bookmark',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='news.user'),
        ),
        migrations.AlterField(
            model_name='user',
            name='date_registered',
            field=models.DateField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='firstName',
            field=models.CharField(max_length=50),
        ),
    ]

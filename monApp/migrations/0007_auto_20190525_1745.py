# Generated by Django 2.1.7 on 2019-05-25 15:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('monApp', '0006_articletype_img'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='article',
            name='dir',
        ),
        migrations.AlterField(
            model_name='article',
            name='date',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]

# Generated by Django 3.2.11 on 2022-01-13 12:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog_app', '0012_comment_parent'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='image_link',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='post',
            name='image',
            field=models.FileField(null=True, upload_to='profile_pics'),
        ),
    ]
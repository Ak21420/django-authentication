# Generated by Django 4.0.1 on 2022-01-10 13:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog_app', '0003_alter_post_options_remove_post_created_at_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='image',
            field=models.ImageField(default=1, upload_to='profile_pics'),
            preserve_default=False,
        ),
    ]

# Generated by Django 4.0.6 on 2022-09-30 09:05

import accounts.models
from django.conf import settings
import django.contrib.auth.validators
import django.core.validators
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('username', models.CharField(help_text='Required. 2 to 150 characters. Letters, digits and @/./+/-/_ only.', max_length=150, validators=[django.core.validators.MinLengthValidator(limit_value=2), django.contrib.auth.validators.UnicodeUsernameValidator()])),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('profile', models.TextField(blank=True)),
                ('avatar', models.ImageField(blank=True, upload_to='accounts/avatar/%Y/%m/%d')),
                ('background', models.ImageField(blank=True, upload_to='accounts/background/%Y/%m/%d')),
                ('visibility', models.CharField(choices=[('public', '전체공개'), ('private', '친구공개'), ('closed', '비공개')], default='public', max_length=7)),
                ('followings', models.ManyToManyField(related_name='followers', related_query_name='follower', to=settings.AUTH_USER_MODEL)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', accounts.models.UserManager()),
            ],
        ),
    ]
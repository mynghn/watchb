# Generated by Django 4.0.6 on 2022-10-13 15:56

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Country',
            fields=[
                ('alpha_2', models.CharField(max_length=2, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=17, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Credit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('job', models.CharField(choices=[('director', '감독'), ('writer', '극본'), ('actor', '배우')], max_length=8)),
                ('cameo_type', models.CharField(blank=True, choices=[('special', '특별출연'), ('writer', '극본'), ('friend', '우정출연')], max_length=7)),
                ('role_name', models.CharField(blank=True, max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Genre',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=10, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Movie',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tmdb_id', models.IntegerField(blank=True, null=True, unique=True)),
                ('kmdb_id', models.CharField(blank=True, max_length=7, null=True, unique=True)),
                ('title', models.CharField(max_length=50)),
                ('original_title', models.CharField(blank=True, max_length=100)),
                ('release_date', models.DateField(blank=True, null=True)),
                ('production_year', models.IntegerField(blank=True, null=True)),
                ('running_time', models.DurationField(blank=True, null=True)),
                ('synopsys', models.TextField(blank=True)),
                ('film_rating', models.CharField(blank=True, choices=[('ALL', '전체관람가'), ('12', '12세이상관람가'), ('15', '15세이상관람가'), ('18', '청소년관람불가'), ('R18', '제한상영가')], max_length=3)),
                ('countries', models.ManyToManyField(blank=True, to='movies.country')),
                ('genres', models.ManyToManyField(blank=True, to='movies.genre')),
            ],
        ),
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tmdb_id', models.IntegerField(blank=True, null=True, unique=True)),
                ('kmdb_id', models.CharField(blank=True, max_length=8, null=True, unique=True)),
                ('name', models.CharField(blank=True, max_length=30)),
                ('en_name', models.CharField(blank=True, max_length=50)),
                ('biography', models.TextField(blank=True)),
                ('avatar_url', models.URLField(blank=True, null=True, unique=True)),
                ('filmography', models.ManyToManyField(related_name='crews', through='movies.Credit', to='movies.movie')),
            ],
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('comment', models.TextField()),
                ('has_spoiler', models.BooleanField(default=False)),
                ('movie', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='movies.movie')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Wishlist',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('movie', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='wishlisted', to='movies.movie')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='wishlists', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Video',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=200, null=True)),
                ('site', models.CharField(choices=[('youtube', 'YouTube')], max_length=7)),
                ('external_id', models.CharField(max_length=11)),
                ('movie', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='movies.movie')),
            ],
        ),
        migrations.CreateModel(
            name='Still',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image_url', models.URLField()),
                ('movie', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='movies.movie')),
            ],
        ),
        migrations.CreateModel(
            name='ReviewLike',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('review', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='liked', to='movies.review')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='review_likes', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Rating',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('score', models.FloatField(choices=[(0.5, '최악이에요'), (1.0, '싫어요'), (1.5, '재미없어요'), (2.0, '별로예요'), (2.5, '부족해요'), (3.0, '보통이에요'), (3.5, '볼만해요'), (4.0, '재미있어요'), (4.5, '훌륭해요!'), (5.0, '최고예요!')])),
                ('movie', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ratings', to='movies.movie')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ratings', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Poster',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image_url', models.URLField()),
                ('is_main', models.BooleanField()),
                ('movie', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='movies.movie')),
            ],
        ),
        migrations.CreateModel(
            name='PersonLike',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('person', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='liked', to='movies.person')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='person_likes', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='credit',
            name='movie',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='credits', to='movies.movie'),
        ),
        migrations.AddField(
            model_name='credit',
            name='person',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='credits_history', to='movies.person'),
        ),
        migrations.CreateModel(
            name='Blocklist',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('movie', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='blocklisted', to='movies.movie')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='blocklists', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddConstraint(
            model_name='wishlist',
            constraint=models.UniqueConstraint(fields=('user', 'movie'), name='one_wishlist_per_user_movie'),
        ),
        migrations.AddConstraint(
            model_name='video',
            constraint=models.UniqueConstraint(fields=('movie', 'title'), name='unique_title_in_movie'),
        ),
        migrations.AddConstraint(
            model_name='video',
            constraint=models.UniqueConstraint(fields=('movie', 'site', 'external_id'), name='unique_video_in_movie'),
        ),
        migrations.AddConstraint(
            model_name='still',
            constraint=models.UniqueConstraint(fields=('movie', 'image_url'), name='unique_still_in_movie'),
        ),
        migrations.AddConstraint(
            model_name='reviewlike',
            constraint=models.UniqueConstraint(fields=('user', 'review'), name='one_like_per_user_review'),
        ),
        migrations.AddConstraint(
            model_name='review',
            constraint=models.UniqueConstraint(fields=('user', 'movie'), name='one_review_per_user_movie'),
        ),
        migrations.AddConstraint(
            model_name='rating',
            constraint=models.UniqueConstraint(fields=('user', 'movie'), name='one_rating_per_user_movie'),
        ),
        migrations.AddConstraint(
            model_name='poster',
            constraint=models.UniqueConstraint(fields=('movie', 'image_url'), name='unique_poster_in_movie'),
        ),
        migrations.AddConstraint(
            model_name='personlike',
            constraint=models.UniqueConstraint(fields=('user', 'person'), name='one_like_per_user_person'),
        ),
        migrations.AddConstraint(
            model_name='blocklist',
            constraint=models.UniqueConstraint(fields=('user', 'movie'), name='one_blocklist_per_user_movie'),
        ),
    ]
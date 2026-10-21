from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('stories', '0005_remove_story_image_story_cover'),
    ]

    operations = [
        migrations.AddField(
            model_name='genre',
            name='audience',
            field=models.CharField(
                choices=[('kids', 'Kids'), ('adults', 'Adults'), ('both', 'Kids and adults')],
                default='both', max_length=10,
            ),
        ),
        migrations.AddField(
            model_name='genre',
            name='emoji',
            field=models.CharField(blank=True, max_length=8),
        ),
        migrations.AddField(
            model_name='story',
            name='audience',
            field=models.CharField(
                choices=[('kids', 'Kids'), ('adults', 'Adults (18+)')],
                db_index=True, default='adults', max_length=10,
                help_text='Adult stories are hidden from the kids section and from anyone who has not confirmed they are 18 or older.',
            ),
        ),
        migrations.AddField(
            model_name='story',
            name='age_group',
            field=models.CharField(
                blank=True,
                choices=[('3-5', 'Ages 3 to 5'), ('6-8', 'Ages 6 to 8'), ('9-12', 'Ages 9 to 12')],
                max_length=5, help_text='Kids stories only.',
            ),
        ),
        migrations.AddField(
            model_name='story',
            name='moral',
            field=models.TextField(blank=True, help_text='Kids stories only: the lesson shown after the story.'),
        ),
        migrations.AddField(
            model_name='story',
            name='content_warning',
            field=models.CharField(
                blank=True, max_length=200,
                help_text='Adult stories only, for example "Violence, grief".',
            ),
        ),
        migrations.AddField(
            model_name='story',
            name='views',
            field=models.PositiveIntegerField(default=0, editable=False),
        ),
        migrations.AlterField(
            model_name='story',
            name='slug',
            field=models.SlugField(blank=True, max_length=270, unique=True),
        ),
        migrations.AlterField(
            model_name='story',
            name='excerpt',
            field=models.TextField(blank=True, help_text='Left empty, it is taken from the start of the story.'),
        ),
        migrations.AddIndex(
            model_name='story',
            index=models.Index(fields=['audience', 'status'], name='story_aud_status_idx'),
        ),
        migrations.CreateModel(
            name='Bookmark',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('story', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bookmarks', to='stories.story')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bookmarks', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['-created_at']},
        ),
        migrations.AddConstraint(
            model_name='bookmark',
            constraint=models.UniqueConstraint(fields=('user', 'story'), name='unique_bookmark_per_user_story'),
        ),
    ]

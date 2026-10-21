from rest_framework import serializers

from .models import Genre, Story


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ['name', 'slug', 'emoji', 'audience']


class StoryListSerializer(serializers.ModelSerializer):
    genre = serializers.CharField(source='genre.name', allow_null=True, default=None)
    genre_slug = serializers.CharField(source='genre.slug', allow_null=True, default=None)
    author = serializers.CharField(source='author.username', allow_null=True, default=None)
    age_group_label = serializers.CharField(source='get_age_group_display', read_only=True)
    reading_time = serializers.IntegerField(read_only=True)
    url = serializers.SerializerMethodField()

    class Meta:
        model = Story
        fields = [
            'title', 'slug', 'url', 'excerpt', 'cover', 'genre', 'genre_slug', 'author',
            'audience', 'age_group', 'age_group_label', 'reading_time', 'featured',
            'created_at',
        ]

    def get_url(self, obj):
        request = self.context.get('request')
        path = obj.get_absolute_url()
        return request.build_absolute_uri(path) if request else path


class StoryDetailSerializer(StoryListSerializer):
    class Meta(StoryListSerializer.Meta):
        fields = StoryListSerializer.Meta.fields + [
            'content', 'moral', 'content_warning', 'views',
        ]

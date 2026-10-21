"""Read-only JSON API. It follows the same age rules as the website."""
from rest_framework import generics
from rest_framework.permissions import AllowAny

from .access import adult_confirmed, visible_stories
from .models import Genre, Story
from .serializers import GenreSerializer, StoryDetailSerializer, StoryListSerializer


class StoryListAPI(generics.ListAPIView):
    """GET /api/stories/?audience=kids&genre=fantasy&age=6-8&q=dragon"""
    serializer_class = StoryListSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        qs = visible_stories(self.request)
        params = self.request.query_params
        if params.get('audience') in (Story.KIDS, Story.ADULTS):
            qs = qs.filter(audience=params['audience'])
        if params.get('genre'):
            qs = qs.filter(genre__slug=params['genre'])
        if params.get('age') in dict(Story.AGE_CHOICES):
            qs = qs.filter(age_group=params['age'])
        if params.get('q'):
            qs = qs.search(params['q'])
        return qs.order_by('-featured', '-created_at')


class StoryDetailAPI(generics.RetrieveAPIView):
    serializer_class = StoryDetailSerializer
    permission_classes = [AllowAny]
    lookup_field = 'slug'

    def get_queryset(self):
        # Hidden adult stories answer 404, so their existence is not revealed.
        return visible_stories(self.request)


class GenreListAPI(generics.ListAPIView):
    serializer_class = GenreSerializer
    permission_classes = [AllowAny]
    pagination_class = None

    def get_queryset(self):
        if adult_confirmed(self.request):
            return Genre.objects.all()
        return Genre.objects.for_audience(Story.KIDS)

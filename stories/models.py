from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils.text import Truncator, slugify


class GenreQuerySet(models.QuerySet):
    def for_audience(self, audience):
        """Genres that belong in the given section (kids or adults)."""
        return self.filter(audience__in=[audience, Genre.BOTH])


class Genre(models.Model):
    KIDS = 'kids'
    ADULTS = 'adults'
    BOTH = 'both'
    AUDIENCE_CHOICES = [
        (KIDS, 'Kids'),
        (ADULTS, 'Adults'),
        (BOTH, 'Kids and adults'),
    ]

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=110, unique=True)
    audience = models.CharField(max_length=10, choices=AUDIENCE_CHOICES, default=BOTH)
    emoji = models.CharField(max_length=8, blank=True)

    objects = GenreQuerySet.as_manager()

    class Meta:
        ordering = ['name']
        verbose_name = 'Genre'
        verbose_name_plural = 'Genres'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('stories:genre_list', kwargs={'slug': self.slug})


class StoryQuerySet(models.QuerySet):
    def published(self):
        return self.filter(status=Story.PUBLISHED)

    def kids(self):
        return self.filter(audience=Story.KIDS)

    def adults(self):
        return self.filter(audience=Story.ADULTS)

    def search(self, text):
        """Every word must appear in the title, excerpt, text or genre name."""
        qs = self
        for term in (text or '').split()[:5]:
            qs = qs.filter(
                models.Q(title__icontains=term)
                | models.Q(excerpt__icontains=term)
                | models.Q(content__icontains=term)
                | models.Q(genre__name__icontains=term)
            )
        return qs


class Story(models.Model):
    DRAFT = 'draft'
    PUBLISHED = 'published'
    STATUS_CHOICES = [(DRAFT, 'Draft'), (PUBLISHED, 'Published')]

    KIDS = 'kids'
    ADULTS = 'adults'
    AUDIENCE_CHOICES = [(KIDS, 'Kids'), (ADULTS, 'Adults (18+)')]

    AGE_CHOICES = [
        ('3-5', 'Ages 3 to 5'),
        ('6-8', 'Ages 6 to 8'),
        ('9-12', 'Ages 9 to 12'),
    ]

    title = models.CharField(max_length=250)
    slug = models.SlugField(max_length=270, unique=True, blank=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    genre = models.ForeignKey(
        Genre, on_delete=models.SET_NULL, null=True, related_name='stories'
    )
    excerpt = models.TextField(
        blank=True, help_text='Left empty, it is taken from the start of the story.'
    )
    content = models.TextField()
    cover = models.ImageField(upload_to='covers/%Y/%m/%d/', blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PUBLISHED)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    featured = models.BooleanField(default=False)

    # Audience. New stories default to ADULTS so that a story can never reach
    # children by accident: an editor has to opt a story in to the kids section.
    audience = models.CharField(
        max_length=10, choices=AUDIENCE_CHOICES, default=ADULTS, db_index=True,
        help_text='Adult stories are hidden from the kids section and from anyone '
                  'who has not confirmed they are 18 or older.',
    )
    age_group = models.CharField(
        max_length=5, choices=AGE_CHOICES, blank=True, help_text='Kids stories only.'
    )
    moral = models.TextField(
        blank=True, help_text='Kids stories only: the lesson shown after the story.'
    )
    content_warning = models.CharField(
        max_length=200, blank=True,
        help_text='Adult stories only, for example "Violence, grief".',
    )
    views = models.PositiveIntegerField(default=0, editable=False)

    objects = StoryQuerySet.as_manager()

    class Meta:
        ordering = ['-featured', '-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['slug']),
            models.Index(fields=['audience', 'status'], name='story_aud_status_idx'),
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('stories:detail', kwargs={'slug': self.slug})

    @property
    def is_kids(self):
        return self.audience == self.KIDS

    @property
    def reading_time(self):
        """Whole minutes at about 200 words a minute, never less than 1."""
        return max(1, round(len(self.content.split()) / 200))

    def clean(self):
        errors = {}
        genre = self.genre if self.genre_id else None
        if self.audience == self.KIDS:
            if not self.age_group:
                errors['age_group'] = 'Choose an age group for a kids story.'
            if genre and genre.audience == Genre.ADULTS:
                errors['genre'] = f'"{genre}" is an adults-only genre. Pick a kids genre.'
        elif genre and genre.audience == Genre.KIDS:
            errors['genre'] = f'"{genre}" is a kids-only genre. Pick an adults genre.'
        if errors:
            raise ValidationError(errors)

    def _make_unique_slug(self):
        base = slugify(self.title)[:250] or 'story'
        slug, n = base, 2
        while Story.objects.exclude(pk=self.pk).filter(slug=slug).exists():
            suffix = f'-{n}'
            slug = base[:270 - len(suffix)] + suffix
            n += 1
        return slug

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self._make_unique_slug()
        if not self.excerpt and self.content:
            self.excerpt = Truncator(self.content).words(30, truncate='…')
        # Keep audience-specific fields from leaking across sections.
        if self.audience == self.KIDS:
            self.content_warning = ''
        else:
            self.age_group = ''
            self.moral = ''
        super().save(*args, **kwargs)


class Bookmark(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookmarks'
    )
    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name='bookmarks')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'story'], name='unique_bookmark_per_user_story'
            ),
        ]

    def __str__(self):
        return f'{self.user} saved {self.story}'

from django.contrib import admin, messages

from .models import Bookmark, Genre, Story


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('emoji', 'name', 'slug', 'audience')
    list_display_links = ('name',)
    list_filter = ('audience',)
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Story)
class StoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'audience', 'age_group', 'genre', 'status', 'featured', 'views', 'created_at')
    list_filter = ('audience', 'age_group', 'status', 'genre', 'featured', 'created_at')
    list_editable = ('featured',)
    search_fields = ('title', 'excerpt', 'content')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'created_at'
    raw_id_fields = ('author',)
    readonly_fields = ('views', 'created_at', 'updated_at')
    actions = ['publish', 'unpublish', 'mark_adults']
    fieldsets = (
        (None, {'fields': ('title', 'slug', 'author', 'genre', 'status', 'featured')}),
        ('Audience', {
            'fields': ('audience', 'age_group', 'moral', 'content_warning'),
            'description': 'Kids stories need an age group and may have a moral. '
                           'Adult stories may have a content warning. Fields for the '
                           'other audience are cleared when you save.',
        }),
        ('Content', {'fields': ('excerpt', 'content', 'cover')}),
        ('Stats and dates', {
            'fields': ('views', 'created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    def save_model(self, request, obj, form, change):
        if not obj.author_id:
            obj.author = request.user
        super().save_model(request, obj, form, change)

    @admin.action(description='Publish selected stories')
    def publish(self, request, queryset):
        n = queryset.update(status=Story.PUBLISHED)
        self.message_user(request, f'{n} stories published.', messages.SUCCESS)

    @admin.action(description='Move selected stories to drafts')
    def unpublish(self, request, queryset):
        n = queryset.update(status=Story.DRAFT)
        self.message_user(request, f'{n} stories moved to drafts.', messages.SUCCESS)

    # There is deliberately no bulk "mark as kids" action: every kids story needs
    # an age group and a person deciding it is suitable. Moving to adults is the
    # safe direction, so it can be done in bulk.
    @admin.action(description='Mark selected stories as adults (18+)')
    def mark_adults(self, request, queryset):
        count = 0
        for story in queryset:
            story.audience = Story.ADULTS
            story.save()  # save() clears the kids-only fields
            count += 1
        self.message_user(request, f'{count} stories moved to the adults section.', messages.SUCCESS)


@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ('user', 'story', 'created_at')
    raw_id_fields = ('user', 'story')
    readonly_fields = ('created_at',)

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import F
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from .access import (
    adult_confirmed, can_access, confirm_adult, gate_redirect, revoke_adult,
    safe_next, visible_stories,
)
from .forms import RegisterForm
from .models import Bookmark, Genre, Story

PAGE_SIZE = 9
SORTS = {'new': '-created_at', 'popular': '-views'}


def _paginate(request, qs):
    """Return (page, querystring-without-page) for the pager links."""
    page = Paginator(qs, PAGE_SIZE).get_page(request.GET.get('page'))
    params = request.GET.copy()
    params.pop('page', None)
    return page, params.urlencode()


def _sorted(request, qs):
    sort = request.GET.get('sort', '')
    if sort in SORTS:
        return qs.order_by(SORTS[sort], '-created_at'), sort
    return qs.order_by('-featured', '-created_at'), ''


# --------------------------------------------------------------------- home

def index(request):
    visible = visible_stories(request)
    adults_total = Story.objects.published().adults().count()
    ctx = {
        'theme': 'neutral',
        'featured': visible.filter(featured=True)[:3],
        'kids_latest': Story.objects.published().kids().select_related('genre')[:4],
        'adults_latest': (
            Story.objects.published().adults().select_related('genre')[:4]
            if adult_confirmed(request) else []
        ),
        'kids_total': Story.objects.published().kids().count(),
        'adults_total': adults_total,
    }
    return render(request, 'stories/index.html', ctx)


# ----------------------------------------------------------------- sections

def _section(request, audience):
    if not can_access(request, audience):
        return gate_redirect(request)

    qs = Story.objects.published().filter(audience=audience).select_related('genre', 'author')
    genres = Genre.objects.for_audience(audience)

    genre = genres.filter(slug=request.GET.get('genre', '')).first()
    if genre:
        qs = qs.filter(genre=genre)

    age = request.GET.get('age', '')
    if audience == Story.KIDS and age in dict(Story.AGE_CHOICES):
        qs = qs.filter(age_group=age)
    else:
        age = ''

    qs, sort = _sorted(request, qs)
    page, base_qs = _paginate(request, qs)

    return render(request, 'stories/story_list.html', {
        'theme': audience,
        'audience': audience,
        'heading': "Kids' Corner" if audience == Story.KIDS else 'Grown-ups',
        'genres': genres,
        'active_genre': genre,
        'active_age': age,
        'active_sort': sort,
        'page_obj': page,
        'base_qs': base_qs,
    })


def kids(request):
    return _section(request, Story.KIDS)


def adults(request):
    return _section(request, Story.ADULTS)


def genre_list(request, slug):
    genre = get_object_or_404(Genre, slug=slug)
    if genre.audience == Genre.ADULTS and not adult_confirmed(request):
        return gate_redirect(request)

    qs, sort = _sorted(request, visible_stories(request).filter(genre=genre))
    page, base_qs = _paginate(request, qs)
    theme = {Genre.KIDS: 'kids', Genre.ADULTS: 'adults'}.get(genre.audience, 'neutral')
    return render(request, 'stories/story_list.html', {
        'theme': theme,
        'audience': '',
        'heading': f'{genre.emoji} {genre.name}'.strip(),
        'genre_page': genre,
        'active_sort': sort,
        'page_obj': page,
        'base_qs': base_qs,
    })


# -------------------------------------------------------------------- story

def story_detail(request, slug):
    story = get_object_or_404(
        Story.objects.published().select_related('genre', 'author'), slug=slug
    )
    if not can_access(request, story.audience):
        return gate_redirect(request)

    # Count a story once per browser session so refreshes do not inflate views.
    viewed = request.session.get('viewed', [])
    if story.pk not in viewed:
        Story.objects.filter(pk=story.pk).update(views=F('views') + 1)
        request.session['viewed'] = (viewed + [story.pk])[-50:]

    related = []
    if story.genre_id:
        related = (
            visible_stories(request)
            .filter(audience=story.audience, genre_id=story.genre_id)
            .exclude(pk=story.pk)[:3]
        )
    bookmarked = (
        request.user.is_authenticated
        and Bookmark.objects.filter(user=request.user, story=story).exists()
    )
    return render(request, 'stories/detail.html', {
        'theme': story.audience,
        'story': story,
        'related': related,
        'bookmarked': bookmarked,
    })


def search(request):
    q = request.GET.get('q', '').strip()[:100]
    qs = visible_stories(request).search(q) if q else Story.objects.none()
    page, base_qs = _paginate(request, qs.order_by('-featured', '-created_at'))
    return render(request, 'stories/search.html', {
        'theme': 'neutral', 'q': q, 'page_obj': page, 'base_qs': base_qs,
    })


# ----------------------------------------------------------- age gate / mode

def age_gate(request):
    target = safe_next(request, reverse('stories:adults'))
    if adult_confirmed(request):
        return redirect(target)
    if request.method == 'POST':
        if request.POST.get('confirm') == 'yes':
            confirm_adult(request)
            return redirect(target)
        return redirect('stories:kids')
    return render(request, 'stories/age_gate.html', {'theme': 'neutral', 'next': target})


@require_POST
def kids_mode(request):
    revoke_adult(request)
    messages.info(request, 'Back to kids mode. Adult stories are hidden again.')
    return redirect('stories:kids')


# ----------------------------------------------------------------- accounts

def register(request):
    if request.user.is_authenticated:
        return redirect('stories:index')
    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, f'Welcome, {user.get_username()}!')
        return redirect(safe_next(request, reverse('stories:index')))
    return render(request, 'stories/register.html', {
        'theme': 'neutral', 'form': form, 'next': request.GET.get('next', ''),
    })


@login_required
def bookmarks(request):
    qs = visible_stories(request).filter(bookmarks__user=request.user)
    qs = qs.order_by('-bookmarks__created_at')
    page, base_qs = _paginate(request, qs)
    return render(request, 'stories/story_list.html', {
        'theme': 'neutral',
        'audience': '',
        'heading': 'Saved stories',
        'page_obj': page,
        'base_qs': base_qs,
        'empty_text': 'You have not saved any stories yet. Tap "Save" on a story to keep it here.',
    })


@login_required
@require_POST
def toggle_bookmark(request, slug):
    # visible_stories hides adult stories from kids mode, so they cannot be saved either.
    story = get_object_or_404(visible_stories(request), slug=slug)
    bookmark, created = Bookmark.objects.get_or_create(user=request.user, story=story)
    if created:
        messages.success(request, 'Saved to your list.')
    else:
        bookmark.delete()
        messages.info(request, 'Removed from your list.')
    return redirect(safe_next(request, story.get_absolute_url()))

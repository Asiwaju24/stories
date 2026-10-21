from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from .models import Bookmark, Genre, Story

User = get_user_model()


def make_story(title, audience=Story.KIDS, genre=None, **extra):
    if audience == Story.KIDS:
        extra.setdefault('age_group', '6-8')
    return Story.objects.create(
        title=title, content=extra.pop('content', 'Once upon a time. ' * 20),
        audience=audience, genre=genre, **extra,
    )


class BaseCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.kids_genre = Genre.objects.create(name='Bedtime', slug='bedtime', audience=Genre.KIDS)
        cls.adult_genre = Genre.objects.create(name='Horror', slug='horror', audience=Genre.ADULTS)
        cls.both_genre = Genre.objects.create(name='Fantasy', slug='fantasy', audience=Genre.BOTH)
        cls.kid = make_story('Sleepy Fox', genre=cls.kids_genre)
        cls.adult = make_story('Dark Manor', Story.ADULTS, cls.adult_genre,
                               content_warning='Violence')
        cls.draft = make_story('Hidden Draft', status=Story.DRAFT)

    def confirm_adult(self):
        self.client.post(reverse('stories:age_gate'), {'confirm': 'yes'})


class ModelTests(BaseCase):
    def test_default_audience_is_adults(self):
        s = Story.objects.create(title='No audience set', content='x')
        self.assertEqual(s.audience, Story.ADULTS)

    def test_slug_and_excerpt_generated_and_unique(self):
        a = Story.objects.create(title='Same Title', content='word ' * 100)
        b = Story.objects.create(title='Same Title', content='other')
        self.assertEqual(a.slug, 'same-title')
        self.assertEqual(b.slug, 'same-title-2')
        self.assertTrue(a.excerpt.endswith('…'))

    def test_kids_requires_age_group(self):
        s = Story(title='t', content='c', audience=Story.KIDS)
        with self.assertRaises(ValidationError):
            s.full_clean()

    def test_genre_audience_must_match(self):
        s = Story(title='t', content='c', audience=Story.KIDS, age_group='3-5', genre=self.adult_genre)
        with self.assertRaises(ValidationError):
            s.full_clean()
        s = Story(title='t2', content='c', audience=Story.ADULTS, genre=self.kids_genre)
        with self.assertRaises(ValidationError):
            s.full_clean()

    def test_save_clears_fields_of_other_audience(self):
        s = make_story('Mixed', Story.ADULTS, moral='m', age_group='3-5', content_warning='cw')
        self.assertEqual((s.moral, s.age_group), ('', ''))
        k = make_story('Mixed kids', Story.KIDS, content_warning='cw')
        self.assertEqual(k.content_warning, '')

    def test_search_requires_every_word(self):
        self.assertEqual(list(Story.objects.search('sleepy fox')), [self.kid])
        self.assertEqual(list(Story.objects.search('sleepy manor')), [])


class AccessTests(BaseCase):
    def test_home_leaks_no_adult_titles(self):
        r = self.client.get(reverse('stories:index'))
        self.assertContains(r, 'Sleepy Fox')
        self.assertNotContains(r, 'Dark Manor')

    def test_adult_section_redirects_to_gate(self):
        r = self.client.get(reverse('stories:adults'))
        self.assertRedirects(r, f"{reverse('stories:age_gate')}?next={reverse('stories:adults')}")

    def test_adult_story_redirects_to_gate(self):
        r = self.client.get(self.adult.get_absolute_url())
        self.assertEqual(r.status_code, 302)
        self.assertIn(reverse('stories:age_gate'), r['Location'])

    def test_confirming_opens_adult_content_and_kids_mode_closes_it(self):
        self.confirm_adult()
        self.assertContains(self.client.get(reverse('stories:adults')), 'Dark Manor')
        self.assertContains(self.client.get(self.adult.get_absolute_url()), 'Violence')
        self.client.post(reverse('stories:kids_mode'))
        self.assertEqual(self.client.get(reverse('stories:adults')).status_code, 302)

    def test_declining_goes_to_kids(self):
        r = self.client.post(reverse('stories:age_gate'), {'confirm': 'no'})
        self.assertRedirects(r, reverse('stories:kids'))
        self.assertEqual(self.client.get(reverse('stories:adults')).status_code, 302)

    def test_gate_ignores_offsite_next(self):
        r = self.client.post(reverse('stories:age_gate'), {'confirm': 'yes', 'next': 'https://evil.example/'})
        self.assertRedirects(r, reverse('stories:adults'), fetch_redirect_response=False)

    def test_search_and_genre_respect_gate(self):
        r = self.client.get(reverse('stories:search'), {'q': 'manor'})
        self.assertNotContains(r, 'Dark Manor')
        self.assertEqual(self.client.get(self.adult_genre.get_absolute_url()).status_code, 302)
        self.confirm_adult()
        self.assertContains(self.client.get(reverse('stories:search'), {'q': 'manor'}), 'Dark Manor')

    def test_drafts_never_shown(self):
        self.assertEqual(self.client.get(self.draft.get_absolute_url()).status_code, 404)
        self.assertNotContains(self.client.get(reverse('stories:kids')), 'Hidden Draft')

    def test_kids_filters(self):
        make_story('Tiny Tale', age_group='3-5')
        r = self.client.get(reverse('stories:kids'), {'age': '3-5'})
        self.assertContains(r, 'Tiny Tale')
        self.assertNotContains(r, 'Sleepy Fox')

    def test_view_counted_once_per_session(self):
        self.client.get(self.kid.get_absolute_url())
        self.client.get(self.kid.get_absolute_url())
        self.kid.refresh_from_db()
        self.assertEqual(self.kid.views, 1)


class ApiTests(BaseCase):
    def test_anonymous_api_only_returns_kids(self):
        data = self.client.get(reverse('stories:api_stories')).json()
        self.assertEqual([s['slug'] for s in data['results']], ['sleepy-fox'])

    def test_adult_detail_is_404_until_confirmed(self):
        url = reverse('stories:api_story', kwargs={'slug': self.adult.slug})
        self.assertEqual(self.client.get(url).status_code, 404)
        self.confirm_adult()
        self.assertEqual(self.client.get(url).json()['content_warning'], 'Violence')

    def test_genres_filtered(self):
        names = [g['name'] for g in self.client.get(reverse('stories:api_genres')).json()]
        self.assertIn('Bedtime', names)
        self.assertNotIn('Horror', names)

    def test_api_is_read_only(self):
        r = self.client.post(reverse('stories:api_stories'), {'title': 'x'})
        self.assertEqual(r.status_code, 405)


class AccountTests(BaseCase):
    def test_bookmark_requires_login(self):
        r = self.client.post(reverse('stories:bookmark', kwargs={'slug': self.kid.slug}))
        self.assertEqual(r.status_code, 302)
        self.assertEqual(Bookmark.objects.count(), 0)

    def test_bookmark_toggle_and_list(self):
        user = User.objects.create_user('reader', password='pw-12345-xyz')
        self.client.force_login(user)
        url = reverse('stories:bookmark', kwargs={'slug': self.kid.slug})
        self.client.post(url)
        self.assertContains(self.client.get(reverse('stories:bookmarks')), 'Sleepy Fox')
        self.client.post(url)
        self.assertEqual(Bookmark.objects.count(), 0)

    def test_cannot_bookmark_hidden_adult_story(self):
        self.client.force_login(User.objects.create_user('r2', password='pw-12345-xyz'))
        r = self.client.post(reverse('stories:bookmark', kwargs={'slug': self.adult.slug}))
        self.assertEqual(r.status_code, 404)

    def test_register_logs_in(self):
        r = self.client.post(reverse('stories:register'), {
            'username': 'newbie', 'password1': 'a-Strong-pass-93', 'password2': 'a-Strong-pass-93',
        })
        self.assertRedirects(r, reverse('stories:index'))
        self.assertTrue(User.objects.filter(username='newbie').exists())

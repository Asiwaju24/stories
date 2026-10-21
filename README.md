# StoryTell

A Django story-reading site with separate sections for **kids** and **adults**.

- **Kids' Corner**: stories sorted by age (3–5, 6–8, 9–12) and genre, each with an optional "What we learned" moral.
- **Grown-ups**: stories with mature themes and content warnings, behind a self-declared 18+ confirmation.
- Search, genre pages, saved stories for logged-in readers, a read-only JSON API, and a customised admin.

## Quick start

Requires Python 3.11+.

```bash
python -m venv env
# Windows:  env\Scripts\activate
# macOS/Linux:  source env/bin/activate
pip install -r requirements.txt

python manage.py migrate
python manage.py createsuperuser
python manage.py seed_stories      # optional: genres and sample stories
python manage.py runserver
```

Open http://127.0.0.1:8000/ and the admin at http://127.0.0.1:8000/admin/.

## How the kids and adults sections work

- Every story has an **audience**: `kids` or `adults`. New stories default to **adults**, so nothing reaches children unless an editor opts it in.
- Kids stories need an age group. Adult stories can carry a content warning. Fields for the other audience are cleared on save.
- Adult stories are hidden everywhere (home page, search, genre pages, saved list and API) until the visitor confirms they are 18 or older. The confirmation lasts until the browser closes, and "Switch to kids mode" revokes it.
- The age gate is a **courtesy for shared devices, not identity verification**. No ID or date of birth is collected. If you need real age assurance, this needs a different design.
- Accounts take only a username and a password.

## Adding stories

Use the admin: **Stories → Add story**. Pick the audience, then fill in the age group (kids) or content warning (adults). Leave the excerpt and slug empty and they are generated for you.

`python manage.py seed_stories` is safe to run repeatedly. It never overwrites a story whose text you have edited.

## API (read-only)

| Endpoint | Description |
| --- | --- |
| `GET /api/stories/` | Paginated list. Filters: `audience`, `genre`, `age`, `q` |
| `GET /api/stories/<slug>/` | One story |
| `GET /api/genres/` | Genres |

The API follows the same age rules as the website. Clients that have not confirmed they are 18+ only receive kids content, and hidden adult stories return 404.

## Configuration

Local development needs no configuration. For production set these environment variables:

| Variable | Purpose |
| --- | --- |
| `DJANGO_DEBUG` | Set to `0` in production (default is on) |
| `DJANGO_SECRET_KEY` | Required when debug is off |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated hostnames |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | Comma-separated origins, e.g. `https://example.com` |
| `DJANGO_BEHIND_PROXY` | Set to `1` only if a proxy that terminates HTTPS sets `X-Forwarded-Proto` |

With debug off, HTTPS redirects, secure cookies and HSTS are enabled. Also run `python manage.py collectstatic`, and serve `static/` and `media/` with your web server or a static-file service, because Django does not serve them in production.

## Tests

```bash
python manage.py test stories
```

## Project layout

```
manage.py
storytell/            project settings and root URLs
stories/
  models.py           Genre, Story, Bookmark
  access.py           the 18+ gate and visibility rules
  views.py, urls.py   website pages
  api.py, serializers.py   JSON API
  admin.py            admin configuration
  management/commands/seed_stories.py
  templates/          HTML templates
  tests.py
static/               CSS and JavaScript
```

## Not committed to git

`db.sqlite3`, `media/`, `staticfiles/`, virtual environments and `.env` files are listed in `.gitignore`. The database holds user accounts and password hashes, so keep it out of the repository. Each developer creates their own with `migrate`.

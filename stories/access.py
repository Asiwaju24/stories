"""Who may see adult content.

The adult section is gated by a self-declared "I am 18 or older" confirmation
stored in the session. It lasts until the browser closes, or until the person
switches back to kids mode or logs out. It is a courtesy gate for families
sharing a device, not identity verification.
"""
from urllib.parse import urlencode

from django.shortcuts import redirect
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme

from .models import Story

ADULT_SESSION_KEY = 'adult_confirmed'


def adult_confirmed(request):
    return bool(request.session.get(ADULT_SESSION_KEY, False))


def confirm_adult(request):
    request.session[ADULT_SESSION_KEY] = True
    request.session.set_expiry(0)  # until the browser closes


def revoke_adult(request):
    request.session.pop(ADULT_SESSION_KEY, None)


def can_access(request, audience):
    return audience != Story.ADULTS or adult_confirmed(request)


def visible_stories(request):
    """Published stories this visitor is allowed to see."""
    qs = Story.objects.published().select_related('genre', 'author')
    if not adult_confirmed(request):
        qs = qs.filter(audience=Story.KIDS)
    return qs


def gate_redirect(request):
    query = urlencode({'next': request.get_full_path()})
    return redirect(f"{reverse('stories:age_gate')}?{query}")


def safe_next(request, fallback):
    target = request.POST.get('next') or request.GET.get('next') or ''
    if target and url_has_allowed_host_and_scheme(
        target, allowed_hosts={request.get_host()}, require_https=request.is_secure()
    ):
        return target
    return fallback

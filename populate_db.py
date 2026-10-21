"""Superseded by the seed_stories management command.

Run:  python manage.py seed_stories

The old script created an "admin" user with a password that was never hashed,
so that login could not work. Create a real one with:
    python manage.py createsuperuser
"""
import os

import django
from django.core.management import call_command

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'storytell.settings')
django.setup()

if __name__ == '__main__':
    call_command('seed_stories')

from .access import adult_confirmed
from .models import Story


def site(request):
    return {
        'adult_confirmed': adult_confirmed(request),
        'age_choices': Story.AGE_CHOICES,
    }

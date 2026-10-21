from django.contrib.auth.forms import UserCreationForm


class RegisterForm(UserCreationForm):
    """Username and password only. We do not ask for an email or a date of birth."""

    class Meta(UserCreationForm.Meta):
        fields = ('username',)

from django import forms
from django.contrib.auth.forms import AuthenticationForm


class PagLaumAuthenticationForm(AuthenticationForm):
    """Styled authentication form for the Pag-Laum mental wellness login screen."""

    remember_me = forms.BooleanField(
        required=False,
        initial=False,
        label="Remember me on this device",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update(
            {
                "class": "form-input",
                "placeholder": "Enter your username",
                "autocomplete": "username",
            }
        )
        self.fields["password"].widget.attrs.update(
            {
                "class": "form-input has-toggle",
                "placeholder": "Enter your password",
                "autocomplete": "current-password",
            }
        )

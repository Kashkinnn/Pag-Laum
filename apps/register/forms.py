from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class PagLaumRegistrationForm(UserCreationForm):
    """Styled registration form for creating a Pag-Laum wellness account."""

    email = forms.EmailField(
        required=False,
        label="Email Address",
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update(
            {
                "class": "form-input",
                "placeholder": "Choose a username",
                "autocomplete": "username",
            }
        )
        self.fields["email"].widget.attrs.update(
            {
                "class": "form-input",
                "placeholder": "you@example.com (optional)",
                "autocomplete": "email",
            }
        )
        self.fields["password1"].widget.attrs.update(
            {
                "class": "form-input has-toggle",
                "placeholder": "Create a password",
                "autocomplete": "new-password",
            }
        )
        self.fields["password2"].widget.attrs.update(
            {
                "class": "form-input has-toggle",
                "placeholder": "Confirm your password",
                "autocomplete": "new-password",
            }
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data.get("email", "")
        if commit:
            user.save()
        return user

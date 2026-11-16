from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.db.models import Q


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


class PagLaumPasswordResetForm(forms.Form):
    """Password recovery form allowing users to reset their password by username or email."""

    identifier = forms.CharField(
        label="Username or Email Address",
        widget=forms.TextInput(
            attrs={
                "class": "form-input",
                "placeholder": "Enter your username or email",
                "autocomplete": "username",
            }
        ),
    )
    new_password1 = forms.CharField(
        label="New Password",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-input has-toggle",
                "placeholder": "Enter a new password",
                "autocomplete": "new-password",
            }
        ),
    )
    new_password2 = forms.CharField(
        label="Confirm New Password",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-input has-toggle",
                "placeholder": "Confirm your new password",
                "autocomplete": "new-password",
            }
        ),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None

    def clean(self):
        cleaned_data = super().clean()
        identifier = (cleaned_data.get("identifier") or "").strip()
        password1 = cleaned_data.get("new_password1")
        password2 = cleaned_data.get("new_password2")

        if password1 and password2 and password1 != password2:
            self.add_error("new_password2", "The two password fields didn't match.")

        if identifier:
            user = User.objects.filter(
                Q(username__iexact=identifier)
                | (Q(email__iexact=identifier) & ~Q(email=""))
            ).first()
            if user is None:
                raise forms.ValidationError(
                    "We couldn't find an account matching that username or email."
                )
            self.user = user

        return cleaned_data

    def save(self):
        self.user.set_password(self.cleaned_data["new_password1"])
        self.user.save()
        return self.user

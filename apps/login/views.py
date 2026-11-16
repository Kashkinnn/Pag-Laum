from django.contrib.auth import login, logout
from django.shortcuts import redirect, render

from .forms import PagLaumAuthenticationForm, PagLaumPasswordResetForm


def login_view(request):
    """Handles user login for Pag-Laum."""
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        form = PagLaumAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            request.session.pop("is_guest", None)
            request.session.pop("guest_name", None)
            login(request, user)
            if not form.cleaned_data.get("remember_me"):
                request.session.set_expiry(0)
            return redirect("home")
    else:
        form = PagLaumAuthenticationForm()

    return render(request, "login/login.html", {"form": form})


def guest_login_view(request):
    """Allows anonymous access to Pag-Laum without creating or saving an account."""
    if request.user.is_authenticated:
        return redirect("home")

    request.session["is_guest"] = True
    request.session["guest_name"] = "Guest"
    return redirect("home")


def forgot_password_view(request):
    """Handles password recovery for Pag-Laum accounts."""
    if request.user.is_authenticated:
        return redirect("home")

    reset_success = False
    reset_username = ""

    if request.method == "POST":
        form = PagLaumPasswordResetForm(request.POST)
        if form.is_valid():
            user = form.save()
            reset_success = True
            reset_username = user.username
    else:
        form = PagLaumPasswordResetForm()

    return render(
        request,
        "login/forgot_password.html",
        {
            "form": form,
            "reset_success": reset_success,
            "reset_username": reset_username,
        },
    )


def logout_session_view(request):
    """Logs out an authenticated user or clears an anonymous guest session."""
    logout(request)
    return redirect("login")

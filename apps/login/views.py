from django.contrib.auth import login
from django.shortcuts import redirect, render

from .forms import PagLaumAuthenticationForm


def login_view(request):
    """Handles user login for Pag-Laum."""
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        form = PagLaumAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if not form.cleaned_data.get("remember_me"):
                request.session.set_expiry(0)
            return redirect("home")
    else:
        form = PagLaumAuthenticationForm()

    return render(request, "login/login.html", {"form": form})

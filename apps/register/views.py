from django.contrib.auth import login
from django.shortcuts import redirect, render

from .forms import PagLaumRegistrationForm


def register_view(request):
    """Handles new user account creation for Pag-Laum."""
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        form = PagLaumRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("home")
    else:
        form = PagLaumRegistrationForm()

    return render(request, "register/register.html", {"form": form})

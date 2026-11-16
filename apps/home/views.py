from functools import wraps

from django.shortcuts import redirect, render

from .data import CRISIS_HOTLINES, EPISODE_GUIDES, PSYCHIATRIC_CENTERS


def login_or_guest_required(view_func):
    """Allow access to authenticated users or active anonymous guest sessions."""

    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if request.user.is_authenticated or request.session.get("is_guest"):
            return view_func(request, *args, **kwargs)
        return redirect("login")

    return _wrapped


def _base_context(request, active_page):
    """Build shared navigation and session display context for dashboard screens."""
    is_guest = not request.user.is_authenticated and bool(request.session.get("is_guest"))
    display_name = request.user.username if request.user.is_authenticated else "Anonymous Guest"
    return {
        "active_page": active_page,
        "is_guest": is_guest,
        "display_name": display_name,
        "hotlines_url": "#quick-hotlines",
        "guides_url": "#quick-grounding",
        "centers_url": "#dashboard-overview",
    }


@login_or_guest_required
def home_view(request):
    """Pag-Laum dashboard displaying urgent help options and core navigation modules."""
    context = _base_context(request, "dashboard")
    context.update(
        {
            "featured_hotlines": [h for h in CRISIS_HOTLINES if h.get("is_featured")],
            "hotlines_count": len(CRISIS_HOTLINES),
            "guides_count": len(EPISODE_GUIDES),
            "centers_count": len(PSYCHIATRIC_CENTERS),
        }
    )
    return render(request, "home/home.html", context)

from functools import wraps

from django.shortcuts import redirect, render
from django.urls import reverse

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
        "hotlines_url": reverse("hotlines"),
        "guides_url": reverse("what_to_do"),
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


@login_or_guest_required
def hotlines_view(request):
    """Crisis hotline directory screen with region filters and search."""
    selected_region = (request.GET.get("region") or "").strip()
    search_query = (request.GET.get("q") or "").strip()

    filtered_hotlines = CRISIS_HOTLINES
    if selected_region and selected_region != "All Regions":
        filtered_hotlines = [
            h for h in filtered_hotlines if h["region"].lower() == selected_region.lower()
        ]
    if search_query:
        q_lower = search_query.lower()
        filtered_hotlines = [
            h
            for h in filtered_hotlines
            if q_lower in h["name"].lower()
            or q_lower in h["description"].lower()
            or q_lower in h["category"].lower()
            or q_lower in h["region"].lower()
            or any(q_lower in n["phone"].lower() for n in h["numbers"])
        ]

    context = _base_context(request, "hotlines")
    context.update(
        {
            "hotlines": filtered_hotlines,
            "regions": [
                "All Regions",
                "National 24/7",
                "Visayas / Cebu",
                "Metro Manila",
                "Emergency",
            ],
            "selected_region": selected_region or "All Regions",
            "search_query": search_query,
        }
    )
    return render(request, "home/hotlines.html", context)


@login_or_guest_required
def what_to_do_view(request):
    """What To Do episode guides and interactive calming grounding tools."""
    context = _base_context(request, "what_to_do")
    context.update(
        {
            "guides": EPISODE_GUIDES,
            "categories": [
                "All Guides",
                "Anxiety",
                "Grounding",
                "Crisis Safety",
                "Low Mood",
                "Caregiver Guide",
            ],
        }
    )
    return render(request, "home/what_to_do.html", context)

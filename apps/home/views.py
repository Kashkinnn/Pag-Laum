from functools import wraps

from django.conf import settings
from django.shortcuts import redirect, render
from django.urls import reverse

from pag_laum.supabase_client import fetch_table, is_supabase_configured

from .data import CRISIS_HOTLINES, EPISODE_GUIDES, PSYCHIATRIC_CENTERS


def _get_table_with_fallback(table_name: str, fallback_data: list[dict]) -> list[dict]:
    """Fetch rows from Supabase when configured, falling back to curated static data."""
    rows = fetch_table(table_name)
    return rows if rows else fallback_data


def get_hotlines_data() -> list[dict]:
    """Return crisis hotlines from Supabase or local static fallback."""
    return _get_table_with_fallback("crisis_hotlines", CRISIS_HOTLINES)


def get_guides_data() -> list[dict]:
    """Return episode guides from Supabase or local static fallback."""
    return _get_table_with_fallback("episode_guides", EPISODE_GUIDES)


def get_centers_data() -> list[dict]:
    """Return psychiatric centers from Supabase or local static fallback."""
    return _get_table_with_fallback("psychiatric_centers", PSYCHIATRIC_CENTERS)


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
        "centers_url": reverse("centers_map"),
        "supabase_url": getattr(settings, "SUPABASE_URL", ""),
        "supabase_connected": is_supabase_configured(),
    }


@login_or_guest_required
def home_view(request):
    """Pag-Laum dashboard displaying urgent help options and core navigation modules."""
    hotlines = get_hotlines_data()
    guides = get_guides_data()
    centers = get_centers_data()
    context = _base_context(request, "dashboard")
    context.update(
        {
            "featured_hotlines": [h for h in hotlines if h.get("is_featured")],
            "hotlines_count": len(hotlines),
            "guides_count": len(guides),
            "centers_count": len(centers),
        }
    )
    return render(request, "home/home.html", context)


@login_or_guest_required
def hotlines_view(request):
    """Crisis hotline directory screen with region filters and search."""
    selected_region = (request.GET.get("region") or "").strip()
    search_query = (request.GET.get("q") or "").strip()

    filtered_hotlines = get_hotlines_data()
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
            "guides": get_guides_data(),
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


@login_or_guest_required
def centers_map_view(request):
    """Psychiatric centers OpenStreetMap locator and nearest facility finder."""
    context = _base_context(request, "centers")
    context.update(
        {
            "centers": get_centers_data(),
            "regions": [
                "All Regions",
                "Visayas / Cebu",
                "Metro Manila",
                "Mindanao",
            ],
        }
    )
    return render(request, "home/centers_map.html", context)

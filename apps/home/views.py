from datetime import date
from functools import wraps
import json

from django.conf import settings
from django.db.models import OuterRef, Subquery
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from pag_laum.supabase_client import fetch_table, is_supabase_configured

from .data import (
    CRISIS_HOTLINES,
    EPISODE_GUIDES,
    HOTLINE_CENTER_REFERRALS,
    PSYCHIATRIC_CENTERS,
)
from .models import (
    CrisisHotline,
    EpisodeGuide,
    JournalEntry,
    PsychiatricCenter,
    ScheduleEvent,
    WellnessNote,
    WellnessReminder,
)


def ensure_relational_data_seeded() -> None:
    """Idempotently seed PsychiatricCenter, CrisisHotline (with FK), and EpisodeGuide rows."""
    needs_centers = PsychiatricCenter.objects.count() < len(PSYCHIATRIC_CENTERS)
    needs_linked_hotlines = CrisisHotline.objects.filter(center__isnull=False).count() == 0
    needs_guides = EpisodeGuide.objects.count() < len(EPISODE_GUIDES)

    if not (needs_centers or needs_linked_hotlines or needs_guides):
        return

    centers_by_slug = {}
    for center_data in PSYCHIATRIC_CENTERS:
        center_obj, _ = PsychiatricCenter.objects.update_or_create(
            slug=center_data["id"],
            defaults={
                "name": center_data["name"],
                "city": center_data["city"],
                "region": center_data["region"],
                "address": center_data["address"],
                "phone": center_data["phone"],
                "dial": center_data["dial"],
                "hours": center_data["hours"],
                "services": center_data["services"],
                "lat": center_data["lat"],
                "lng": center_data["lng"],
                "emergency_available": center_data["emergency_available"],
            },
        )
        centers_by_slug[center_obj.slug] = center_obj

    for hotline_data in CRISIS_HOTLINES:
        target_center_slug = HOTLINE_CENTER_REFERRALS.get(hotline_data["id"])
        target_center = centers_by_slug.get(target_center_slug)
        CrisisHotline.objects.update_or_create(
            slug=hotline_data["id"],
            defaults={
                "name": hotline_data["name"],
                "region": hotline_data["region"],
                "category": hotline_data["category"],
                "availability": hotline_data["availability"],
                "description": hotline_data["description"],
                "numbers": hotline_data["numbers"],
                "is_featured": hotline_data["is_featured"],
                "center": target_center,
            },
        )

    for guide_data in EPISODE_GUIDES:
        EpisodeGuide.objects.update_or_create(
            slug=guide_data["id"],
            defaults={
                "title": guide_data["title"],
                "category": guide_data["category"],
                "urgency": guide_data["urgency"],
                "duration": guide_data["duration"],
                "summary": guide_data["summary"],
                "steps": guide_data["steps"],
                "reassurance": guide_data["reassurance"],
            },
        )


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
        "referral_join_url": reverse("referral_network_join"),
        "dispatch_subquery_url": reverse("dispatch_centers_subquery"),
        "journaling_url": reverse("journaling"),
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


def build_referral_join_queryset(selected_region: str = ""):
    """Build a SQL JOIN queryset combining CrisisHotline rows with their parent PsychiatricCenter."""
    qs = (
        CrisisHotline.objects.select_related("center")
        .filter(center__isnull=False)
        .order_by("region", "name")
    )
    if selected_region and selected_region != "All Regions":
        qs = qs.filter(region__iexact=selected_region)
    return qs


@login_or_guest_required
def referral_network_join_view(request):
    """Display CrisisHotline joined with its receiving PsychiatricCenter via select_related()."""
    ensure_relational_data_seeded()
    selected_region = (request.GET.get("region") or "").strip()

    join_queryset = build_referral_join_queryset(selected_region)
    generated_sql = str(join_queryset.query)
    hotline_referrals = list(join_queryset)
    distinct_centers_count = len({h.center_id for h in hotline_referrals})

    context = _base_context(request, "referral_join")
    context.update(
        {
            "hotline_referrals": hotline_referrals,
            "total_joined_count": len(hotline_referrals),
            "distinct_centers_count": distinct_centers_count,
            "regions": [
                "All Regions",
                "National 24/7",
                "Visayas / Cebu",
                "Metro Manila",
                "Emergency",
            ],
            "selected_region": selected_region or "All Regions",
            "generated_sql": generated_sql,
        }
    )
    return render(request, "home/referral_join.html", context)


def build_dispatch_inner_queryset(filter_mode: str = "all_linked"):
    """Build the inner CrisisHotline queryset returning linked PsychiatricCenter IDs."""
    inner_hotlines = CrisisHotline.objects.filter(center__isnull=False)
    if filter_mode == "featured":
        inner_hotlines = inner_hotlines.filter(is_featured=True)
    return inner_hotlines.values("center_id")


def build_dispatch_subquery_queryset(filter_mode: str = "all_linked"):
    """Build a SQL SUBQUERY queryset filtering PsychiatricCenter using nested CrisisHotline SELECT."""
    inner_center_ids = build_dispatch_inner_queryset(filter_mode)

    primary_hotline_name_sq = (
        CrisisHotline.objects.filter(center=OuterRef("pk"))
        .order_by("-is_featured", "id")
        .values("name")[:1]
    )
    primary_hotline_category_sq = (
        CrisisHotline.objects.filter(center=OuterRef("pk"))
        .order_by("-is_featured", "id")
        .values("category")[:1]
    )

    if filter_mode == "walkin_only":
        return (
            PsychiatricCenter.objects.exclude(id__in=Subquery(inner_center_ids))
            .order_by("region", "name")
        )

    return (
        PsychiatricCenter.objects.filter(id__in=Subquery(inner_center_ids))
        .annotate(
            primary_hotline_name=Subquery(primary_hotline_name_sq),
            primary_hotline_category=Subquery(primary_hotline_category_sq),
        )
        .order_by("region", "name")
    )


@login_or_guest_required
def dispatch_centers_subquery_view(request):
    """Display PsychiatricCenter records filtered via an explicit nested CrisisHotline Subquery."""
    ensure_relational_data_seeded()
    filter_mode = (request.GET.get("mode") or "all_linked").strip()
    if filter_mode not in {"all_linked", "featured", "walkin_only"}:
        filter_mode = "all_linked"

    inner_qs = build_dispatch_inner_queryset(filter_mode)
    subquery_queryset = build_dispatch_subquery_queryset(filter_mode)
    generated_sql = str(subquery_queryset.query)
    inner_sql = str(inner_qs.query)

    centers = list(subquery_queryset)
    total_centers_count = PsychiatricCenter.objects.count()
    all_linked_count = build_dispatch_subquery_queryset("all_linked").count()
    featured_count = build_dispatch_subquery_queryset("featured").count()
    walkin_count = build_dispatch_subquery_queryset("walkin_only").count()

    context = _base_context(request, "dispatch_subquery")
    context.update(
        {
            "centers": centers,
            "filter_mode": filter_mode,
            "total_centers_count": total_centers_count,
            "matched_centers_count": len(centers),
            "all_linked_count": all_linked_count,
            "featured_count": featured_count,
            "walkin_count": walkin_count,
            "generated_sql": generated_sql,
            "inner_sql": inner_sql,
        }
    )
    return render(request, "home/dispatch_subquery.html", context)


def _parse_iso_date(raw_value: str | None) -> date | None:
    """Parse an ISO YYYY-MM-DD date string safely."""
    if not raw_value:
        return None
    try:
        return date.fromisoformat(str(raw_value).strip())
    except (ValueError, TypeError):
        return None


def _serialize_schedule(event: ScheduleEvent) -> dict:
    return {
        "id": str(event.id),
        "title": event.title,
        "event_date": event.event_date.isoformat(),
        "event_time": event.event_time,
        "category": event.category,
        "notes": event.notes,
    }


def _serialize_journal(entry: JournalEntry) -> dict:
    return {
        "id": str(entry.id),
        "entry_date": entry.entry_date.isoformat(),
        "title": entry.title,
        "mood": entry.mood,
        "content": entry.content,
    }


def _serialize_note(note: WellnessNote) -> dict:
    return {
        "id": str(note.id),
        "title": note.title,
        "content": note.content,
        "tag": note.tag,
        "created_at": note.created_at.strftime("%b %d, %Y"),
    }


def _serialize_reminder(reminder: WellnessReminder) -> dict:
    return {
        "id": str(reminder.id),
        "title": reminder.title,
        "due_date": reminder.due_date.isoformat() if reminder.due_date else "",
        "due_time": reminder.due_time,
        "is_completed": reminder.is_completed,
    }


@login_or_guest_required
def journaling_view(request):
    """Personal Journaling workspace with calendar scheduling, daily journal, notes, and reminders."""
    context = _base_context(request, "journaling")

    if request.user.is_authenticated:
        initial_data = {
            "schedules": [
                _serialize_schedule(ev)
                for ev in ScheduleEvent.objects.filter(user=request.user)
            ],
            "journals": [
                _serialize_journal(entry)
                for entry in JournalEntry.objects.filter(user=request.user)
            ],
            "notes": [
                _serialize_note(note)
                for note in WellnessNote.objects.filter(user=request.user)
            ],
            "reminders": [
                _serialize_reminder(rem)
                for rem in WellnessReminder.objects.filter(user=request.user)
            ],
        }
        storage_mode = "account"
    else:
        initial_data = {
            "schedules": [],
            "journals": [],
            "notes": [],
            "reminders": [],
        }
        storage_mode = "local"

    context.update(
        {
            "storage_mode": storage_mode,
            "journaling_api_url": reverse("journaling_api"),
            "initial_journal_data": initial_data,
            "today_iso": date.today().isoformat(),
        }
    )
    return render(request, "home/journaling.html", context)


@login_or_guest_required
@require_POST
def journaling_api_view(request):
    """JSON persistence endpoint for authenticated users' journaling items."""
    if not request.user.is_authenticated:
        return JsonResponse(
            {"error": "Guest entries are stored privately on your device."},
            status=403,
        )

    try:
        payload = json.loads(request.body.decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        return JsonResponse({"error": "Invalid JSON payload."}, status=400)

    action = (payload.get("action") or "").strip()

    if action == "create_schedule":
        title = (payload.get("title") or "").strip()
        event_date = _parse_iso_date(payload.get("event_date"))
        if not title or not event_date:
            return JsonResponse({"error": "Title and valid date are required."}, status=400)
        event = ScheduleEvent.objects.create(
            user=request.user,
            title=title[:200],
            event_date=event_date,
            event_time=(payload.get("event_time") or "").strip()[:20],
            category=(payload.get("category") or "Self-Care").strip()[:60] or "Self-Care",
            notes=(payload.get("notes") or "").strip(),
        )
        return JsonResponse({"item": _serialize_schedule(event)}, status=201)

    if action == "delete_schedule":
        deleted, _ = ScheduleEvent.objects.filter(
            id=payload.get("id"), user=request.user
        ).delete()
        if not deleted:
            return JsonResponse({"error": "Schedule item not found."}, status=404)
        return JsonResponse({"deleted": True})

    if action == "create_journal":
        title = (payload.get("title") or "").strip()
        content = (payload.get("content") or "").strip()
        entry_date = _parse_iso_date(payload.get("entry_date")) or date.today()
        if not title or not content:
            return JsonResponse({"error": "Title and journal entry text are required."}, status=400)
        entry = JournalEntry.objects.create(
            user=request.user,
            entry_date=entry_date,
            title=title[:200],
            mood=(payload.get("mood") or "Calm").strip()[:40] or "Calm",
            content=content,
        )
        return JsonResponse({"item": _serialize_journal(entry)}, status=201)

    if action == "delete_journal":
        deleted, _ = JournalEntry.objects.filter(
            id=payload.get("id"), user=request.user
        ).delete()
        if not deleted:
            return JsonResponse({"error": "Journal entry not found."}, status=404)
        return JsonResponse({"deleted": True})

    if action == "create_note":
        title = (payload.get("title") or "").strip()
        content = (payload.get("content") or "").strip()
        if not title or not content:
            return JsonResponse({"error": "Note title and content are required."}, status=400)
        note = WellnessNote.objects.create(
            user=request.user,
            title=title[:160],
            content=content,
            tag=(payload.get("tag") or "Reflection").strip()[:60] or "Reflection",
        )
        return JsonResponse({"item": _serialize_note(note)}, status=201)

    if action == "delete_note":
        deleted, _ = WellnessNote.objects.filter(
            id=payload.get("id"), user=request.user
        ).delete()
        if not deleted:
            return JsonResponse({"error": "Note not found."}, status=404)
        return JsonResponse({"deleted": True})

    if action == "create_reminder":
        title = (payload.get("title") or "").strip()
        if not title:
            return JsonResponse({"error": "Reminder text is required."}, status=400)
        reminder = WellnessReminder.objects.create(
            user=request.user,
            title=title[:200],
            due_date=_parse_iso_date(payload.get("due_date")),
            due_time=(payload.get("due_time") or "").strip()[:20],
        )
        return JsonResponse({"item": _serialize_reminder(reminder)}, status=201)

    if action == "toggle_reminder":
        reminder = WellnessReminder.objects.filter(
            id=payload.get("id"), user=request.user
        ).first()
        if reminder is None:
            return JsonResponse({"error": "Reminder not found."}, status=404)
        reminder.is_completed = not reminder.is_completed
        reminder.save(update_fields=["is_completed"])
        return JsonResponse({"item": _serialize_reminder(reminder)})

    if action == "delete_reminder":
        deleted, _ = WellnessReminder.objects.filter(
            id=payload.get("id"), user=request.user
        ).delete()
        if not deleted:
            return JsonResponse({"error": "Reminder not found."}, status=404)
        return JsonResponse({"deleted": True})

    return JsonResponse({"error": "Unsupported journaling action."}, status=400)

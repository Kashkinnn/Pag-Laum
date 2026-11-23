from django.conf import settings
from django.db import models


class CrisisHotline(models.Model):
    """Curated crisis hotline entry mirrored in Supabase."""

    slug = models.SlugField(unique=True)
    name = models.CharField(max_length=200)
    region = models.CharField(max_length=100)
    category = models.CharField(max_length=120)
    availability = models.CharField(max_length=100, default="24/7")
    description = models.TextField()
    numbers = models.JSONField(default=list)
    is_featured = models.BooleanField(default=False)
    center = models.ForeignKey(
        "PsychiatricCenter",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="hotlines",
    )

    def __str__(self) -> str:
        return self.name


class EpisodeGuide(models.Model):
    """Structured 'What To Do' episode coping guide mirrored in Supabase."""

    slug = models.SlugField(unique=True)
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=100)
    urgency = models.CharField(max_length=100)
    duration = models.CharField(max_length=60)
    summary = models.TextField()
    steps = models.JSONField(default=list)
    reassurance = models.TextField()

    def __str__(self) -> str:
        return self.title


class PsychiatricCenter(models.Model):
    """Psychiatric center / mental health facility location mirrored in Supabase."""

    slug = models.SlugField(unique=True)
    name = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    region = models.CharField(max_length=100)
    address = models.TextField()
    phone = models.CharField(max_length=60)
    dial = models.CharField(max_length=60)
    hours = models.CharField(max_length=200)
    services = models.JSONField(default=list)
    lat = models.FloatField()
    lng = models.FloatField()
    emergency_available = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.name


class ScheduleEvent(models.Model):
    """User-owned calendar scheduling event for appointments and self-care."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="schedule_events",
    )
    title = models.CharField(max_length=200)
    event_date = models.DateField()
    event_time = models.CharField(max_length=20, blank=True, default="")
    category = models.CharField(max_length=60, default="Self-Care")
    notes = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["event_date", "event_time", "id"]

    def __str__(self) -> str:
        return f"{self.event_date} - {self.title}"


class JournalEntry(models.Model):
    """User-owned personal day-to-day journal entry."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="journal_entries",
    )
    entry_date = models.DateField()
    title = models.CharField(max_length=200)
    mood = models.CharField(max_length=40, default="Calm")
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-entry_date", "-created_at"]

    def __str__(self) -> str:
        return f"{self.entry_date} - {self.title}"


class WellnessNote(models.Model):
    """User-owned quick personal note."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="wellness_notes",
    )
    title = models.CharField(max_length=160)
    content = models.TextField()
    tag = models.CharField(max_length=60, default="Reflection")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.title


class WellnessReminder(models.Model):
    """User-owned checkable personal wellness reminder."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="wellness_reminders",
    )
    title = models.CharField(max_length=200)
    due_date = models.DateField(null=True, blank=True)
    due_time = models.CharField(max_length=20, blank=True, default="")
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["is_completed", "due_date", "due_time", "-created_at"]

    def __str__(self) -> str:
        return self.title

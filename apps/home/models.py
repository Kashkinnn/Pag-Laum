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

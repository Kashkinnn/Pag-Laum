import json
from unittest.mock import MagicMock, patch

from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse

from pag_laum.supabase_client import build_rest_url, fetch_table

from .models import CrisisHotline, EpisodeGuide, PsychiatricCenter
from .views import get_hotlines_data


class HomeScreensTests(TestCase):
    """Tests for Pag-Laum dashboard, crisis hotlines, episode guides, centers map, and logout."""

    def setUp(self):
        self.login_url = reverse("login")
        self.guest_login_url = reverse("guest_login")
        self.logout_url = reverse("logout")
        self.home_url = reverse("home")
        self.hotlines_url = reverse("hotlines")
        self.what_to_do_url = reverse("what_to_do")
        self.centers_map_url = reverse("centers_map")
        self.protected_urls = [
            self.home_url,
            self.hotlines_url,
            self.what_to_do_url,
            self.centers_map_url,
        ]
        self.user = User.objects.create_user(
            username="dashboard_member",
            password="MemberPassword123!",
        )

    def test_unauthenticated_non_guest_redirects_to_login(self):
        for url in self.protected_urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertRedirects(response, self.login_url)

    def test_guest_user_can_access_all_dashboard_screens(self):
        guest_response = self.client.get(self.guest_login_url)
        self.assertRedirects(guest_response, self.home_url)

        for url in self.protected_urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, "Guest Mode")

    def test_authenticated_user_sees_dashboard_hotlines_guides_and_centers(self):
        self.client.force_login(self.user)

        home_resp = self.client.get(self.home_url)
        self.assertEqual(home_resp.status_code, 200)
        self.assertContains(home_resp, "dashboard_member")
        self.assertContains(home_resp, "Crisis Hotline List")
        self.assertContains(home_resp, "What To Do (Guides)")
        self.assertContains(home_resp, "Psychiatric Center Map")

        hotlines_resp = self.client.get(self.hotlines_url)
        self.assertEqual(hotlines_resp.status_code, 200)
        self.assertContains(hotlines_resp, "1553")
        self.assertContains(hotlines_resp, "Tawag Paglaum")

        guides_resp = self.client.get(self.what_to_do_url)
        self.assertEqual(guides_resp.status_code, 200)
        self.assertContains(guides_resp, "Panic Attack")
        self.assertContains(guides_resp, "5-4-3-2-1 Sensory Grounding")

        centers_resp = self.client.get(self.centers_map_url)
        self.assertEqual(centers_resp.status_code, 200)
        self.assertContains(centers_resp, "Vicente Sotto Memorial Medical Center")
        self.assertContains(centers_resp, "National Center for Mental Health")
        self.assertContains(centers_resp, "Find Nearest Center to Me")

    def test_logout_clears_authenticated_and_guest_sessions(self):
        self.client.get(self.guest_login_url)
        self.assertTrue(self.client.session.get("is_guest"))

        logout_resp = self.client.post(self.logout_url)
        self.assertRedirects(logout_resp, self.login_url)
        self.assertFalse(self.client.session.get("is_guest", False))

        blocked_resp = self.client.get(self.home_url)
        self.assertRedirects(blocked_resp, self.login_url)


class SupabaseIntegrationTests(TestCase):
    """Tests for Supabase REST configuration, fallback behavior, and home models."""

    def test_supabase_project_url_configured(self):
        self.assertEqual(settings.SUPABASE_URL, "https://fcouztcbiaehhdyuwyie.supabase.co")
        self.assertEqual(settings.SUPABASE_PROJECT_REF, "fcouztcbiaehhdyuwyie")

    def test_build_rest_url_points_to_supabase_project(self):
        url = build_rest_url("crisis_hotlines", {"select": "*"})
        self.assertEqual(
            url,
            "https://fcouztcbiaehhdyuwyie.supabase.co/rest/v1/crisis_hotlines?select=%2A",
        )

    @override_settings(SUPABASE_ANON_KEY="")
    def test_fetch_table_falls_back_when_anon_key_missing(self):
        self.assertIsNone(fetch_table("crisis_hotlines"))
        hotlines = get_hotlines_data()
        self.assertTrue(len(hotlines) >= 1)
        self.assertTrue(any("1553" in str(h) for h in hotlines))

    @override_settings(SUPABASE_ANON_KEY="test-anon-key")
    @patch("urllib.request.urlopen")
    def test_fetch_table_queries_supabase_when_key_configured(self, mock_urlopen):
        mock_rows = [
            {
                "id": "ncmh-1553",
                "name": "NCMH Crisis Hotline",
                "region": "National 24/7",
                "availability": "24/7",
                "description": "National crisis line",
                "numbers": [{"label": "Toll-Free", "phone": "1553", "dial": "1553"}],
                "is_featured": True,
            }
        ]
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.read.return_value = json.dumps(mock_rows).encode("utf-8")
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        rows = fetch_table("crisis_hotlines")

        self.assertEqual(rows, mock_rows)
        sent_request = mock_urlopen.call_args[0][0]
        self.assertEqual(
            sent_request.full_url,
            "https://fcouztcbiaehhdyuwyie.supabase.co/rest/v1/crisis_hotlines?select=%2A",
        )
        self.assertEqual(sent_request.get_header("Apikey"), "test-anon-key")

    def test_home_models_can_store_hotlines_guides_and_centers(self):
        hotline = CrisisHotline.objects.create(
            slug="ncmh-1553",
            name="NCMH Crisis Hotline",
            region="National 24/7",
            category="Mental Health Crisis",
            availability="24/7",
            description="24/7 national crisis line",
            numbers=[{"label": "Landline", "phone": "1553", "dial": "1553"}],
            is_featured=True,
        )
        guide = EpisodeGuide.objects.create(
            slug="panic-attack",
            title="Panic Attack & Acute Anxiety",
            category="Anxiety",
            urgency="Immediate Calm",
            duration="3-5 mins",
            summary="Calming breathing guide",
            steps=[{"title": "Breathe", "detail": "Exhale slowly for 6 seconds."}],
            reassurance="You are safe right now.",
        )
        center = PsychiatricCenter.objects.create(
            slug="vsmmc-cbs",
            name="Vicente Sotto Memorial Medical Center",
            city="Cebu City",
            region="Visayas / Cebu",
            address="B. Rodriguez St, Cebu City",
            phone="(032) 253-9891",
            dial="+63322539891",
            hours="24/7 Emergency",
            services=["24/7 Emergency Triage"],
            lat=10.3075,
            lng=123.8919,
            emergency_available=True,
        )

        self.assertEqual(str(hotline), "NCMH Crisis Hotline")
        self.assertEqual(str(guide), "Panic Attack & Acute Anxiety")
        self.assertEqual(str(center), "Vicente Sotto Memorial Medical Center")
        self.assertEqual(CrisisHotline.objects.count(), 1)
        self.assertEqual(EpisodeGuide.objects.count(), 1)
        self.assertEqual(PsychiatricCenter.objects.count(), 1)

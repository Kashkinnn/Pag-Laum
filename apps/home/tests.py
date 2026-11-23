import json
from unittest.mock import MagicMock, patch

from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse

from pag_laum.supabase_client import build_rest_url, fetch_table

from .models import (
    CrisisHotline,
    EpisodeGuide,
    JournalEntry,
    PsychiatricCenter,
    ScheduleEvent,
    WellnessNote,
    WellnessReminder,
)
from .views import (
    build_dispatch_subquery_queryset,
    build_referral_join_queryset,
    ensure_relational_data_seeded,
    get_hotlines_data,
)


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
        self.referral_join_url = reverse("referral_network_join")
        self.dispatch_subquery_url = reverse("dispatch_centers_subquery")
        self.journaling_url = reverse("journaling")
        self.protected_urls = [
            self.home_url,
            self.hotlines_url,
            self.what_to_do_url,
            self.centers_map_url,
            self.referral_join_url,
            self.dispatch_subquery_url,
            self.journaling_url,
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


class RelationalDatabaseOperationsTests(TestCase):
    """Tests for Django ORM SQL JOIN (select_related) and SQL SUBQUERY (Subquery + OuterRef) features."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="relational_tester",
            password="TesterPassword123!",
        )
        self.client.force_login(self.user)
        self.referral_join_url = reverse("referral_network_join")
        self.dispatch_subquery_url = reverse("dispatch_centers_subquery")

    def test_join_query_and_view_display_both_tables(self):
        ensure_relational_data_seeded()
        join_qs = build_referral_join_queryset()
        sql = str(join_qs.query)

        self.assertIn("INNER JOIN", sql)
        self.assertIn("home_app_psychiatriccenter", sql)
        self.assertIn("home_app_crisishotline", sql)
        self.assertEqual(join_qs.count(), 7)

        response = self.client.get(self.referral_join_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Hotline-to-Hospital Referral Network")
        self.assertContains(response, "Tawag Paglaum")
        self.assertContains(response, "Vicente Sotto Memorial Medical Center")
        self.assertContains(response, "B. Rodriguez St")
        self.assertContains(response, "Direct Hospital Referral")
        self.assertNotContains(response, "ORM &amp; Compiled SQL Verification")

        filtered_resp = self.client.get(self.referral_join_url, {"region": "Visayas / Cebu"})
        self.assertEqual(filtered_resp.status_code, 200)
        self.assertEqual(filtered_resp.context["total_joined_count"], 2)
        self.assertEqual(filtered_resp.context["distinct_centers_count"], 1)

    def test_subquery_query_and_view_filter_modes(self):
        ensure_relational_data_seeded()

        all_linked_qs = build_dispatch_subquery_queryset("all_linked")
        featured_qs = build_dispatch_subquery_queryset("featured")
        walkin_qs = build_dispatch_subquery_queryset("walkin_only")

        all_linked_sql = str(all_linked_qs.query)
        walkin_sql = str(walkin_qs.query)

        self.assertIn("IN (SELECT", all_linked_sql)
        self.assertIn("WHERE", all_linked_sql)
        self.assertIn("primary_hotline_name", all_linked_sql)
        self.assertIn("NOT (", walkin_sql)
        self.assertIn("IN (SELECT", walkin_sql)

        self.assertEqual(all_linked_qs.count(), 4)
        self.assertEqual(featured_qs.count(), 3)
        self.assertEqual(walkin_qs.count(), 3)

        resp_all = self.client.get(self.dispatch_subquery_url, {"mode": "all_linked"})
        self.assertEqual(resp_all.status_code, 200)
        self.assertEqual(resp_all.context["matched_centers_count"], 4)
        self.assertContains(resp_all, "National Center for Mental Health (NCMH) Crisis Hotline")

        resp_featured = self.client.get(self.dispatch_subquery_url, {"mode": "featured"})
        self.assertEqual(resp_featured.status_code, 200)
        self.assertEqual(resp_featured.context["matched_centers_count"], 3)

        resp_walkin = self.client.get(self.dispatch_subquery_url, {"mode": "walkin_only"})
        self.assertEqual(resp_walkin.status_code, 200)
        self.assertEqual(resp_walkin.context["matched_centers_count"], 3)
        self.assertContains(resp_walkin, "Chong Hua Hospital")
        self.assertContains(resp_walkin, "Western Visayas Medical Center")
        self.assertNotContains(resp_all, "Inner Query vs. Outer Query SQL Verification")


class JournalingScreenTests(TestCase):
    """Tests for the Journaling screen (calendar schedules, daily journal, notes, and reminders)."""

    def setUp(self):
        self.journaling_url = reverse("journaling")
        self.journaling_api_url = reverse("journaling_api")
        self.guest_login_url = reverse("guest_login")
        self.user = User.objects.create_user(
            username="journal_member",
            password="JournalPass123!",
        )
        self.other_user = User.objects.create_user(
            username="other_member",
            password="OtherPass123!",
        )

    def test_guest_user_gets_local_storage_journaling_mode_and_cannot_write_to_db(self):
        self.client.get(self.guest_login_url)
        resp = self.client.get(self.journaling_url)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Journaling")
        self.assertContains(resp, "Saved privately on this device only")
        self.assertEqual(resp.context["storage_mode"], "local")

        api_resp = self.client.post(
            self.journaling_api_url,
            data=json.dumps({"action": "create_note", "title": "Hi", "content": "Guest note"}),
            content_type="application/json",
        )
        self.assertEqual(api_resp.status_code, 403)
        self.assertEqual(WellnessNote.objects.count(), 0)

    def test_authenticated_user_crud_for_schedules_journals_notes_and_reminders(self):
        self.client.force_login(self.user)
        page_resp = self.client.get(self.journaling_url)
        self.assertEqual(page_resp.status_code, 200)
        self.assertEqual(page_resp.context["storage_mode"], "account")
        self.assertContains(page_resp, "Care &amp; Wellness Calendar")
        self.assertContains(page_resp, "Personal Day-to-Day Journal")

        # Schedule create + delete
        sched_resp = self.client.post(
            self.journaling_api_url,
            data=json.dumps(
                {
                    "action": "create_schedule",
                    "title": "Counseling Check-in",
                    "event_date": "2026-11-24",
                    "event_time": "14:00",
                    "category": "Therapy",
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(sched_resp.status_code, 201)
        sched_id = sched_resp.json()["item"]["id"]
        self.assertEqual(ScheduleEvent.objects.filter(user=self.user).count(), 1)

        # Journal create
        journal_resp = self.client.post(
            self.journaling_api_url,
            data=json.dumps(
                {
                    "action": "create_journal",
                    "entry_date": "2026-11-23",
                    "title": "Quiet Evening",
                    "mood": "Calm",
                    "content": "Took a slow walk and felt lighter.",
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(journal_resp.status_code, 201)
        journal_id = journal_resp.json()["item"]["id"]
        self.assertEqual(JournalEntry.objects.filter(user=self.user).count(), 1)

        # Note create
        note_resp = self.client.post(
            self.journaling_api_url,
            data=json.dumps(
                {
                    "action": "create_note",
                    "title": "Grounding Words",
                    "tag": "Coping Idea",
                    "content": "This wave will pass.",
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(note_resp.status_code, 201)
        note_id = note_resp.json()["item"]["id"]
        self.assertEqual(WellnessNote.objects.filter(user=self.user).count(), 1)

        # Reminder create + toggle
        rem_resp = self.client.post(
            self.journaling_api_url,
            data=json.dumps(
                {
                    "action": "create_reminder",
                    "title": "Drink a glass of water",
                    "due_date": "2026-11-23",
                    "due_time": "18:00",
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(rem_resp.status_code, 201)
        rem_id = rem_resp.json()["item"]["id"]
        toggle_resp = self.client.post(
            self.journaling_api_url,
            data=json.dumps({"action": "toggle_reminder", "id": rem_id}),
            content_type="application/json",
        )
        self.assertEqual(toggle_resp.status_code, 200)
        self.assertTrue(toggle_resp.json()["item"]["is_completed"])

        # User isolation: another user cannot delete this user's schedule
        self.client.force_login(self.other_user)
        forbidden_del = self.client.post(
            self.journaling_api_url,
            data=json.dumps({"action": "delete_schedule", "id": sched_id}),
            content_type="application/json",
        )
        self.assertEqual(forbidden_del.status_code, 404)
        self.assertEqual(ScheduleEvent.objects.filter(user=self.user).count(), 1)

        # Owner deletes all 4 items cleanly
        self.client.force_login(self.user)
        for action, item_id in [
            ("delete_schedule", sched_id),
            ("delete_journal", journal_id),
            ("delete_note", note_id),
            ("delete_reminder", rem_id),
        ]:
            del_resp = self.client.post(
                self.journaling_api_url,
                data=json.dumps({"action": action, "id": item_id}),
                content_type="application/json",
            )
            self.assertEqual(del_resp.status_code, 200)
        self.assertEqual(ScheduleEvent.objects.count(), 0)
        self.assertEqual(JournalEntry.objects.count(), 0)
        self.assertEqual(WellnessNote.objects.count(), 0)
        self.assertEqual(WellnessReminder.objects.count(), 0)

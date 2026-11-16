from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


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

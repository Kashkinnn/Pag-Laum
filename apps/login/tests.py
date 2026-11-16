from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class LoginViewTests(TestCase):
    """Tests for the Pag-Laum split-card login screen."""

    def setUp(self):
        self.login_url = reverse("login")
        self.home_url = reverse("home")
        self.username = "wellness_user"
        self.password = "StrongPass123!"
        self.user = User.objects.create_user(
            username=self.username,
            password=self.password,
        )

    def test_login_page_renders_split_card_branding(self):
        response = self.client.get(self.login_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "login/login.html")
        self.assertContains(response, "Pag-Laum")
        self.assertContains(response, "Where hope begins")
        self.assertContains(response, "Welcome Back")
        self.assertContains(response, "Confidential Counseling")
        self.assertContains(response, "css/login.css")

    def test_login_with_valid_credentials_redirects_to_home(self):
        response = self.client.post(
            self.login_url,
            {
                "username": self.username,
                "password": self.password,
                "remember_me": "on",
            },
        )

        self.assertRedirects(response, self.home_url)
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_login_without_remember_me_sets_browser_session_expiry(self):
        response = self.client.post(
            self.login_url,
            {
                "username": self.username,
                "password": self.password,
            },
        )

        self.assertRedirects(response, self.home_url)
        self.assertTrue(self.client.session.get_expire_at_browser_close())

    def test_login_with_invalid_credentials_displays_error_alert(self):
        response = self.client.post(
            self.login_url,
            {
                "username": self.username,
                "password": "WrongPassword!",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "alert-error")
        self.assertFalse(response.wsgi_request.user.is_authenticated)

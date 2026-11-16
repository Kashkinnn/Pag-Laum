from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class LoginViewTests(TestCase):
    """Tests for the Pag-Laum split-card login, forgot password, and guest mode."""

    def setUp(self):
        self.login_url = reverse("login")
        self.forgot_password_url = reverse("forgot_password")
        self.guest_login_url = reverse("guest_login")
        self.home_url = reverse("home")
        self.username = "wellness_user"
        self.email = "wellness@paglaum.org"
        self.password = "StrongPass123!"
        self.user = User.objects.create_user(
            username=self.username,
            email=self.email,
            password=self.password,
        )

    def test_login_page_renders_split_card_branding(self):
        response = self.client.get(self.login_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "login/login.html")
        self.assertContains(response, "Pag-Laum")
        self.assertContains(response, "Where hope begins")
        self.assertContains(response, "Welcome Back")
        self.assertContains(response, "24/7 Crisis Hotlines")
        self.assertContains(response, "Continue as Guest (Anonymous)")
        self.assertContains(response, "Forgot password?")
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

    def test_forgot_password_page_renders(self):
        response = self.client.get(self.forgot_password_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "login/forgot_password.html")
        self.assertContains(response, "Reset Your Password")

    def test_forgot_password_updates_user_password(self):
        response = self.client.post(
            self.forgot_password_url,
            {
                "identifier": self.email,
                "new_password1": "NewHopePass456!",
                "new_password2": "NewHopePass456!",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Password updated!")
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("NewHopePass456!"))

    def test_guest_login_sets_session_flag_and_redirects(self):
        response = self.client.get(self.guest_login_url)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, self.home_url)
        self.assertTrue(self.client.session.get("is_guest"))

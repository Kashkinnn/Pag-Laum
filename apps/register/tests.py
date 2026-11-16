from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class RegisterViewTests(TestCase):
    """Tests for the Pag-Laum split-card create account screen."""

    def setUp(self):
        self.register_url = reverse("register")
        self.home_url = reverse("home")

    def test_register_page_renders_split_card_ui(self):
        response = self.client.get(self.register_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "register/register.html")
        self.assertContains(response, "Create Account")
        self.assertContains(response, "Where hope begins")
        self.assertContains(response, "Begin Your Wellness Journey")
        self.assertContains(response, "css/register.css")

    def test_register_creates_user_and_redirects_to_home(self):
        response = self.client.post(
            self.register_url,
            {
                "username": "new_wellness_member",
                "email": "member@paglaum.org",
                "password1": "WellnessPass123!",
                "password2": "WellnessPass123!",
            },
        )

        self.assertRedirects(response, self.home_url)
        created_user = User.objects.get(username="new_wellness_member")
        self.assertEqual(created_user.email, "member@paglaum.org")
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_register_with_mismatched_passwords_shows_error(self):
        response = self.client.post(
            self.register_url,
            {
                "username": "mismatch_user",
                "email": "mismatch@paglaum.org",
                "password1": "WellnessPass123!",
                "password2": "DifferentPass456!",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="mismatch_user").exists())
        self.assertContains(response, "field-error")

    def test_authenticated_user_redirected_to_home(self):
        existing_user = User.objects.create_user(
            username="existing_member",
            password="ExistingUserPass123!",
        )
        self.client.force_login(existing_user)

        response = self.client.get(self.register_url)

        self.assertRedirects(response, self.home_url)

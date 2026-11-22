from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.projects.testing import make_barangay, make_project

from .models import BarangayOfficial


class RegisterTests(TestCase):
    def setUp(self):
        self.lahug = make_barangay("Lahug")

    def data(self, **over):
        d = {"username": "juan", "first_name": "Juan", "last_name": "Cruz", "email": "juan@example.com",
             "password1": "S3cure-pass-42", "password2": "S3cure-pass-42",
             "barangay_code": self.lahug.barangay_code}
        d.update(over)
        return d

    def test_valid_code_registers_official_for_that_barangay(self):
        r = self.client.post(reverse("register"), self.data())
        self.assertRedirects(r, reverse("my_projects"))
        user = get_user_model().objects.get(username="juan")
        self.assertEqual(user.barangay_official.barangay, self.lahug)
        self.assertFalse(user.is_staff)

    def test_code_is_case_and_space_insensitive(self):
        code = f" {self.lahug.barangay_code.lower()} "
        self.client.post(reverse("register"), self.data(barangay_code=code))
        self.assertTrue(BarangayOfficial.objects.filter(barangay=self.lahug).exists())

    def test_wrong_code_is_rejected(self):
        r = self.client.post(reverse("register"), self.data(barangay_code="ZZZZ-ZZZZ"))
        self.assertEqual(r.status_code, 200)
        self.assertFalse(get_user_model().objects.filter(username="juan").exists())

    def test_duplicate_email_rejected(self):
        get_user_model().objects.create_user("other", email="JUAN@example.com", password="x12345678!")
        self.client.post(reverse("register"), self.data())
        self.assertFalse(get_user_model().objects.filter(username="juan").exists())


class MyProjectsTests(TestCase):
    def setUp(self):
        self.mine = make_project("Lahug")
        make_project("Mabolo", project_name="Other barangay")
        user = get_user_model().objects.create_user("lahug", password="pw12345!")
        BarangayOfficial.objects.create(user=user, barangay=self.mine.barangays.first())

    def test_login_required(self):
        self.assertEqual(self.client.get(reverse("my_projects")).status_code, 302)

    def test_scoped_to_own_barangay(self):
        self.client.login(username="lahug", password="pw12345!")
        r = self.client.get(reverse("my_projects"))
        self.assertEqual(list(r.context["projects"]), [self.mine])

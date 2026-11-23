from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import BarangayOfficial
from apps.projects.models import Project
from apps.projects.testing import make_barangay, make_project


class ProjectManagerTests(TestCase):
    def setUp(self):
        U = get_user_model()
        self.lahug = make_barangay("Lahug")
        self.official = U.objects.create_user("lahug", password="pw12345!")
        BarangayOfficial.objects.create(user=self.official, barangay=self.lahug)
        U.objects.create_user("resident", password="pw12345!")
        self.mine = make_project("Lahug", "Sitio A", project_name="Feeding program")
        self.theirs = make_project("Mabolo", project_name="Mabolo roads")
        self.data = {"project_name": "Tutorial sessions", "amount": "75000.50",
                     "project_date": "2026-11-20", "sitio": "Sitio Bagong Silang"}

    def login(self, username="lahug"):
        self.client.login(username=username, password="pw12345!")

    def test_login_and_role_required(self):
        self.assertEqual(self.client.get(reverse("project_create")).status_code, 302)
        self.login("resident")
        self.assertEqual(self.client.get(reverse("project_create")).status_code, 403)

    def test_official_adds_project_for_own_barangay(self):
        self.login()
        r = self.client.post(reverse("project_create"), self.data)
        p = Project.objects.get(project_name="Tutorial sessions")
        self.assertRedirects(r, p.get_absolute_url())
        self.assertEqual(p.status, "approved")
        self.assertEqual(p.project_date, date(2026, 11, 20))
        link = p.barangay_links.get()
        self.assertEqual((link.barangay, link.sitio), (self.lahug, "Sitio Bagong Silang"))

    def test_official_edits_own_project(self):
        self.login()
        url = reverse("project_edit", args=[self.mine.code])
        self.assertContains(self.client.get(url), "Sitio A")  # sitio pre-filled
        self.client.post(url, {**self.data, "project_name": "Feeding program 2"})
        self.mine.refresh_from_db()
        self.assertEqual(self.mine.project_name, "Feeding program 2")
        self.assertEqual(self.mine.barangay_links.get().sitio, "Sitio Bagong Silang")
        self.assertEqual(self.mine.status, "approved")

    def test_cannot_edit_another_barangays_project(self):
        self.login()
        url = reverse("project_edit", args=[self.theirs.code])
        self.assertEqual(self.client.get(url).status_code, 404)
        self.client.post(url, self.data)
        self.theirs.refresh_from_db()
        self.assertEqual(self.theirs.project_name, "Mabolo roads")

    def test_status_cannot_be_changed_here(self):
        self.login()
        self.client.post(reverse("project_edit", args=[self.mine.code]), {**self.data, "status": "completed"})
        self.mine.refresh_from_db()
        self.assertEqual(self.mine.status, "approved")

    def test_validation(self):
        self.login()
        url = reverse("project_create")
        self.client.post(url, {**self.data, "amount": "0"})
        self.client.post(url, {**self.data, "project_name": "feeding PROGRAM"})  # duplicate in barangay
        self.assertFalse(Project.objects.filter(project_name__in=["Tutorial sessions", "feeding PROGRAM"]).exists())

    def test_edit_links_shown_to_officials_only(self):
        self.login()
        self.assertContains(self.client.get(reverse("my_projects")), reverse("project_edit", args=[self.mine.code]))
        self.assertContains(self.client.get(self.mine.get_absolute_url()), "Edit project")
        self.assertNotContains(self.client.get(self.theirs.get_absolute_url()), "Edit project")
        self.client.logout()
        self.assertNotContains(self.client.get(self.mine.get_absolute_url()), "Edit project")

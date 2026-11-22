import re

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import CityOfficial

from .models import Barangay, Project
from .testing import make_barangay, make_project


class ModelTests(TestCase):
    def test_project_code_round_trip(self):
        p = make_project()
        self.assertEqual(p.code, f"LDF-{p.pk:04d}")
        self.assertEqual(Project.pk_from_code(p.code.lower()), p.pk)
        self.assertEqual(Project.pk_from_code(str(p.pk)), p.pk)
        self.assertIsNone(Project.pk_from_code("nonsense"))

    def test_barangay_code_is_random_and_unique(self):
        a, b = make_barangay("Lahug"), make_barangay("Mabolo")
        self.assertRegex(a.barangay_code, r"^[A-Z0-9]{4}-[A-Z0-9]{4}$")
        self.assertNotEqual(a.barangay_code, b.barangay_code)
        old = a.barangay_code
        a.regenerate_code()
        self.assertNotEqual(a.barangay_code, old)


class ProjectScreenTests(TestCase):
    def setUp(self):
        self.p1 = make_project("Lahug", "Sitio Mahayag")
        self.p2 = make_project("Mabolo", "Sitio Riverside", project_name="Feeding program", status="bidding")
        U = get_user_model()
        city = U.objects.create_user("cpdo", password="pw12345!")
        CityOfficial.objects.create(user=city)
        U.objects.create_user("resident", password="pw12345!")

    def test_filters(self):
        r = self.client.get(reverse("project_list"), {"status": "bidding"})
        self.assertEqual(list(r.context["page_obj"]), [self.p2])
        r = self.client.get(reverse("project_list"), {"barangay": self.p1.barangays.first().pk})
        self.assertEqual(list(r.context["page_obj"]), [self.p1])
        r = self.client.get(reverse("project_list"), {"q": "riverside"})
        self.assertEqual(list(r.context["page_obj"]), [self.p2])

    def test_detail_page(self):
        r = self.client.get(self.p1.get_absolute_url())
        self.assertContains(r, "Sitio Mahayag")
        self.assertEqual(self.client.get("/projects/LDF-9999/").status_code, 404)

    def test_only_city_officials_can_update(self):
        url = reverse("update_status", args=[self.p1.code])
        self.assertEqual(self.client.get(url).status_code, 302)  # to login
        self.client.login(username="resident", password="pw12345!")
        self.assertEqual(self.client.get(url).status_code, 403)
        self.client.login(username="cpdo", password="pw12345!")
        self.client.post(url, {"status": "completed"})
        self.p1.refresh_from_db()
        self.assertEqual(self.p1.status, "completed")

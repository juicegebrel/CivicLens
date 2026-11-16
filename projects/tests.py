from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .testing import make_project


class ProjectTests(TestCase):
    def setUp(self):
        self.p1 = make_project(category="Livelihood")
        self.p2 = make_project("Mabolo", "Health and Nutrition", title="Feeding program", status="bidding")
        U = get_user_model()
        self.staff = U.objects.create_user("cpdo", password="pw12345!", is_staff=True)
        U.objects.create_user("resident", password="pw12345!")

    def test_code_generated(self):
        self.assertEqual(self.p1.code, f"LDF-2026-{self.p1.pk:04d}")

    def test_search_by_category_and_status(self):
        r = self.client.get(reverse("project_list"), {"category": "livelihood"})
        self.assertEqual(r.context["result_count"], 1)
        r = self.client.get(reverse("project_list"), {"status": "bidding"})
        self.assertEqual(list(r.context["page_obj"]), [self.p2])

    def test_detail_page(self):
        self.assertEqual(self.client.get(self.p1.get_absolute_url()).status_code, 200)

    def test_only_staff_can_update(self):
        url = reverse("update_status", args=[self.p1.code])
        self.client.login(username="resident", password="pw12345!")
        self.assertEqual(self.client.get(url).status_code, 403)
        self.client.login(username="cpdo", password="pw12345!")
        self.client.post(url, {
            "status": "completed", "progress_percent": 40, "amount_utilized": "25000", "remarks": "Done",
        })
        self.p1.refresh_from_db()
        self.assertEqual((self.p1.status, self.p1.progress_percent), ("completed", 100))
        self.assertEqual(self.p1.updates.count(), 1)
        self.assertEqual(self.p1.amount_utilized, 25000)

    def test_utilized_cannot_exceed_budget(self):
        self.client.login(username="cpdo", password="pw12345!")
        r = self.client.post(reverse("update_status", args=[self.p1.code]), {
            "status": "in_process", "progress_percent": 50, "amount_utilized": "999999999", "remarks": "",
        })
        self.assertEqual(r.status_code, 200)
        self.p1.refresh_from_db()
        self.assertEqual(self.p1.amount_utilized, 0)

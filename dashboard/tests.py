from django.test import TestCase
from django.urls import reverse

from projects.testing import make_project


class DashboardTests(TestCase):
    def setUp(self):
        make_project()
        make_project(title="Seed capital", status="bidding")

    def test_dashboard_renders(self):
        self.assertEqual(self.client.get(reverse("dashboard")).status_code, 200)

    def test_stats_api(self):
        data = self.client.get(reverse("stats_api")).json()
        self.assertEqual(data["total"], 2)
        self.assertEqual(sum(s["count"] for s in data["statuses"]), 2)

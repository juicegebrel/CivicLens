from django.test import TestCase
from django.urls import reverse

from apps.projects.testing import make_project


class DashboardTests(TestCase):
    def setUp(self):
        make_project("Lahug", amount=100000, status="in_process")
        make_project("Mabolo", amount=50000, status="bidding")

    def test_dashboard_renders(self):
        r = self.client.get(reverse("dashboard"))
        self.assertContains(r, "total money allocated")

    def test_funds_and_barangay_stats(self):
        d = self.client.get(reverse("stats_api")).json()
        self.assertEqual(d["total"], 2)
        self.assertEqual(d["total_allocated"], 150000)
        self.assertEqual(d["total_committed"], 100000)
        self.assertEqual(d["committed_percent"], 67)
        self.assertEqual(d["barangays_covered"], 2)
        self.assertEqual(len(d["barangays"]), 2)
        self.assertEqual(len(d["recent"]), 2)

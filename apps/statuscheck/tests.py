from django.test import TestCase
from django.urls import reverse

from apps.projects.testing import make_project


class StatusCheckTests(TestCase):
    def test_found_case_insensitive(self):
        p = make_project()
        r = self.client.get(reverse("status_check"), {"code": p.code.lower()})
        self.assertEqual(r.context["project"], p)

    def test_not_found(self):
        for code in ("nope", "LDF-9999"):
            r = self.client.get(reverse("status_check"), {"code": code})
            self.assertIsNone(r.context["project"])
            self.assertTrue(r.context["searched"])

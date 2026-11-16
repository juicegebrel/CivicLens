from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from projects.testing import make_project

from .models import Profile


class AccountsTests(TestCase):
    def setUp(self):
        self.mine = make_project("Lahug")
        make_project("Mabolo", title="Other barangay")
        self.user = get_user_model().objects.create_user("lahug", password="pw12345!")
        Profile.objects.create(user=self.user, barangay=self.mine.barangay)

    def test_login_required(self):
        self.assertEqual(self.client.get(reverse("my_projects")).status_code, 302)

    def test_my_projects_scoped_to_barangay(self):
        self.client.login(username="lahug", password="pw12345!")
        r = self.client.get(reverse("my_projects"))
        self.assertEqual(list(r.context["projects"]), [self.mine])

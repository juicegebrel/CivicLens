import os
import random
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.accounts.models import BarangayOfficial, CityOfficial
from apps.projects.models import Barangay, BarangayProject, Project, Status

BARANGAYS = ["Lahug", "Guadalupe", "Mabolo", "Banilad", "Apas", "Talamban", "Kasambagan", "Labangon", "Pardo", "Basak San Nicolas"]
SITIOS = ["Sitio Mahayag", "Sitio Riverside", "Sitio Bagong Silang", "Sitio Proper", "Sitio Tabay", "Sitio Maligaya", "Purok 1", "Purok 2"]
TITLES = [
    "Supplemental feeding program", "Barangay health worker training", "Free medical and dental mission",
    "Tutorial and reading program", "Scholarship grants for senior high", "Alternative learning sessions",
    "Skills training for solo parents", "Urban gardening starter kits", "Micro-enterprise seed capital",
    "Senior citizen assistance program", "PWD assistance and ID drive", "Day care learning materials",
    "Emergency response drills and kits", "Disaster awareness drive", "Inter-barangay sports league", "Youth leadership camp",
]


class Command(BaseCommand):
    help = "Load demo barangays, projects and demo accounts."

    def add_arguments(self, parser):
        parser.add_argument("--force", action="store_true", help="Delete existing projects first.")

    def handle(self, *args, **opts):
        if Project.objects.exists() and not opts["force"]:
            self.stdout.write("Projects already exist. Use --force to replace them.")
            return
        Project.objects.all().delete()
        random.seed(7)
        password = os.environ.get("CIVICLENS_DEMO_PASSWORD", "civiclens123")

        barangays = [Barangay.objects.get_or_create(barangay_name=n)[0] for n in BARANGAYS]

        User = get_user_model()
        cpdo, _ = User.objects.get_or_create(username="cpdo", defaults={
            "is_staff": True, "is_superuser": True, "first_name": "CPDO", "last_name": "Staff", "email": "cpdo@example.com"})
        cpdo.set_password(password); cpdo.save()
        CityOfficial.objects.get_or_create(user=cpdo)

        brgy, _ = User.objects.get_or_create(username="brgy_lahug", defaults={
            "first_name": "Lahug", "last_name": "Official", "email": "lahug@example.com"})
        brgy.set_password(password); brgy.save()
        BarangayOfficial.objects.update_or_create(user=brgy, defaults={"barangay": barangays[0]})

        today = timezone.localdate()
        weights = [3, 4, 3, 7, 7, 2, 1]
        for i in range(28):
            p = Project.objects.create(
                project_name=random.choice(TITLES),
                status=random.choices(list(Status), weights=weights)[0],
                amount=Decimal(random.randrange(150, 2500)) * 1000,
                project_date=today - timedelta(days=random.randrange(5, 240)),
            )
            first = barangays[i % 3 if i < 9 else random.randrange(len(barangays))]
            chosen = {first}
            if random.random() < 0.2:
                chosen.add(random.choice(barangays))
            for b in chosen:
                BarangayProject.objects.create(project=p, barangay=b, sitio=random.choice(SITIOS))

        self.stdout.write(self.style.SUCCESS("Demo data loaded."))
        self.stdout.write(f"City official login:     cpdo / {password}")
        self.stdout.write(f"Barangay official login: brgy_lahug / {password}")
        self.stdout.write("\nBarangay registration codes (give these to barangay officials):")
        for b in Barangay.objects.all():
            self.stdout.write(f"  {b.barangay_name:<20} {b.barangay_code}")

import random
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.text import slugify

from apps.accounts.models import Profile
from apps.projects.models import Barangay, Category, Project, Status, StatusUpdate

BARANGAYS = ["Lahug", "Guadalupe", "Mabolo", "Banilad", "Apas", "Talamban", "Kasambagan", "Labangon", "Pardo", "Basak San Nicolas"]

PROJECTS = {
    "Health and Nutrition": ["Supplemental feeding program", "Barangay health worker training", "Free medical and dental mission"],
    "Education and Scholarship": ["Tutorial and reading program", "Scholarship grants for senior high", "Alternative learning sessions"],
    "Livelihood": ["Skills training for solo parents", "Urban gardening starter kits", "Micro-enterprise seed capital"],
    "Social Welfare": ["Senior citizen assistance program", "PWD assistance and ID drive", "Day care learning materials"],
    "Disaster Risk Reduction": ["Emergency response drills and kits", "Early-warning system awareness drive"],
    "Youth and Sports": ["Inter-barangay sports league", "Youth leadership camp"],
}

STAGES = [Status.APPROVED, Status.BIDDING, Status.AWARDED, Status.IN_PROCESS, Status.COMPLETED]


class Command(BaseCommand):
    help = "Load demo barangays, categories, projects and two demo accounts."

    def add_arguments(self, parser):
        parser.add_argument("--force", action="store_true", help="Delete existing projects first.")

    def handle(self, *args, **opts):
        if Project.objects.exists() and not opts["force"]:
            self.stdout.write("Projects already exist. Use --force to replace them.")
            return
        Project.objects.all().delete()
        random.seed(7)

        barangays = [Barangay.objects.get_or_create(name=n)[0] for n in BARANGAYS]
        cats = {n: Category.objects.get_or_create(name=n, defaults={"slug": slugify(n)})[0] for n in PROJECTS}

        User = get_user_model()
        cpdo, _ = User.objects.get_or_create(username="cpdo", defaults={"is_staff": True, "is_superuser": True, "first_name": "CPDO"})
        cpdo.set_password("civiclens123"); cpdo.save()
        brgy, _ = User.objects.get_or_create(username="brgy_lahug", defaults={"first_name": "Lahug"})
        brgy.set_password("civiclens123"); brgy.save()
        Profile.objects.update_or_create(user=brgy, defaults={"barangay": barangays[0]})

        now = timezone.now()
        for i in range(28):
            cat_name = random.choice(list(PROJECTS))
            final = random.choices(
                [*STAGES, Status.ON_HOLD, Status.CANCELLED], weights=[3, 4, 3, 7, 7, 2, 1])[0]
            fy = random.choice([2025, 2026, 2026])
            p = Project.objects.create(
                title=random.choice(PROJECTS[cat_name]),
                description="Non-infrastructure project funded under the Local Development Fund.",
                barangay=barangays[i % 3 if i < 9 else random.randrange(len(barangays))],
                category=cats[cat_name], fiscal_year=fy,
                budget=Decimal(random.randrange(150, 2500)) * 1000,
                start_date=(now - timedelta(days=random.randrange(30, 240))).date(),
                target_end_date=(now + timedelta(days=random.randrange(-20, 180))).date(),
            )
            path = list(STAGES[: STAGES.index(final) + 1]) if final in STAGES else [*STAGES[:4], final]
            if final == Status.CANCELLED:
                path = [*STAGES[:2], final]
            when = now - timedelta(days=len(path) * 12)
            for status in path:
                progress = {"completed": 100, "in_process": random.randrange(20, 90)}.get(status.value, 0)
                u = StatusUpdate.objects.create(project=p, status=status, progress_percent=progress,
                                                remarks=f"Status changed to {status.label.lower()}.", updated_by=cpdo)
                StatusUpdate.objects.filter(pk=u.pk).update(created_at=when)
                when += timedelta(days=random.randrange(5, 14))
            last = path[-1]
            if last == Status.COMPLETED:
                used = p.budget * Decimal(random.randrange(85, 101)) / 100
            elif last in (Status.IN_PROCESS, Status.ON_HOLD):
                used = p.budget * Decimal(progress) / 100 * Decimal(random.randrange(70, 100)) / 100
            else:
                used = Decimal(0)
            Project.objects.filter(pk=p.pk).update(
                status=last.value, progress_percent=progress, amount_utilized=used.quantize(Decimal("0.01"))
            )

        self.stdout.write(self.style.SUCCESS("Demo data loaded."))
        self.stdout.write("Staff login:    cpdo / civiclens123")
        self.stdout.write("Barangay login: brgy_lahug / civiclens123")

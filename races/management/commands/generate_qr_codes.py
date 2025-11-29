from django.core.management.base import BaseCommand
from profiles.models import Profile
import qrcode
import os

class Command(BaseCommand):
    help = "Generate QR codes for all Race profiles that do not already have one."

    def handle(self, *args, **options):
        base_dir = "media/qrcodes/"

        if not os.path.exists(base_dir):
            os.makedirs(base_dir)

        races = Profile.objects.filter(profiletype='RACE')

        for race in races:
            filename = f"race_{race.id}.png"
            filepath = os.path.join(base_dir, filename)

            if os.path.exists(filepath):
                self.stdout.write(self.style.WARNING(f"Exists: {filename}"))
                continue

            join_url = f"https://rekjrc.com/races/{race.id}/join/"

            img = qrcode.make(join_url)
            img.save(filepath)

            self.stdout.write(self.style.SUCCESS(f"Created: {filename}"))

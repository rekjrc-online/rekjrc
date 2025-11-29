import csv
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from races.models import LapMonitorResult

class Command(BaseCommand):
    help = 'Import LapMonitor CSV data into the LapMonitorResult table'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to the LapMonitor CSV file')

    def handle(self, *args, **options):
        csv_file = options['csv_file']

        try:
            with open(csv_file, newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                count = 0

                for row in reader:
                    try:
                        LapMonitorResult.objects.create(
                            session_id=row['Session Id'],
                            session_name=row['Session Name'],
                            session_date=datetime.strptime(row['Session Date'], '%Y-%m-%d %H:%M:%S'),
                            session_kind=row['Session Kind'],
                            session_duration=float(row['Session Duration']),
                            driver_id=row['Driver Id'],
                            driver_name=row['Driver Name'],
                            driver_transponder_id=row['Driver Transponder Id'],
                            driver_rank=int(row['Driver Rank']),
                            lap_index=int(row['Lap Index']),
                            lap_end_time=float(row['Lap End Time']),
                            lap_duration=float(row['Lap Duration']),
                            lap_kind=row['Lap Kind'],
                        )
                        count += 1
                    except Exception as e:
                        self.stderr.write(self.style.ERROR(f"Error on row {count+1}: {e}"))
                        continue

                self.stdout.write(self.style.SUCCESS(f"Successfully imported {count} LapMonitor rows."))

        except FileNotFoundError:
            raise CommandError(f"File '{csv_file}' not found.")

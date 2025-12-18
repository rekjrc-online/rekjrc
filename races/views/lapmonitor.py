from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, render, redirect
from django.views import View
from django.views.generic import View
from ..models import Race, LapMonitorResult
from io import TextIOWrapper
import csv

class LapMonitorUploadView(LoginRequiredMixin, View):
    template_name = "races/lapmonitor_upload.html"

    def get(self, request, race_uuid):
        race = get_object_or_404(Race, uuid=race.uuid)
        if race.human != request.user:
            return redirect("profiles:detail-profile", profile_uuid=race.profile.uuid)
        return render(request, self.template_name, {"race": race})

    def post(self, request, race_uuid):
        race = get_object_or_404(Race, uuid=race.uuid)
        if race.human != request.user:
            return redirect("profiles:detail-profile", profile_uuid=race.profile.uuid)
        file = request.FILES.get("file")
        if not file:
            messages.error(request, "❌ No file selected.")
            return redirect("races:upload_lapmonitor", race_uuid=race.uuid)
        try:
            data = TextIOWrapper(file.file, encoding="utf-8")
            reader = csv.DictReader(data)
            reader.fieldnames = [n.strip().lower().replace(" ", "_") for n in reader.fieldnames]
            created_count = 0
            skipped_count = 0
            for row in reader:
                try:
                    if not row.get("driver_id") or not row.get("lap_index"):
                        skipped_count += 1
                        continue
                    if LapMonitorResult.objects.filter(
                        race=race,
                        driver_id=row.get("driver_id"),
                        lap_index=row.get("lap_index")
                    ).exists():
                        skipped_count += 1
                        continue
                    LapMonitorResult.objects.create(
                        race=race,
                        session_id=row.get("session_id"),
                        session_name=row.get("session_name"),
                        session_date=row.get("session_date"),
                        session_kind=row.get("session_kind"),
                        session_duration=float(row.get("session_duration") or 0),
                        driver_id=row.get("driver_id"),
                        driver_name=row.get("driver_name"),
                        driver_transponder_id=row.get("driver_transponder_id"),
                        driver_rank=int(row.get("driver_rank") or 0),
                        lap_index=int(row.get("lap_index") or 0),
                        lap_end_time=float(row.get("lap_end_time") or 0),
                        lap_duration=float(row.get("lap_duration") or 0),
                        lap_kind=row.get("lap_kind"),
                    )
                    created_count += 1
                except Exception:
                    skipped_count += 1
            messages.success(request, f"✅ Imported {created_count} new results, skipped {skipped_count} rows.")
        except Exception as e:
            messages.error(request, f"❌ Error processing CSV: {e}")
        return redirect("profiles:detail-profile", profile_uuid=race.profile.uuid)

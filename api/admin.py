from django.contrib import admin
from .models import Patient, Doctor, PatientDoctorMapping


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "age", "gender", "owner", "created_at")
    search_fields = ("name", "owner__username", "owner__email")
    list_filter = ("gender",)


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "specialization", "created_at")
    search_fields = ("name", "specialization")


@admin.register(PatientDoctorMapping)
class PatientDoctorMappingAdmin(admin.ModelAdmin):
    list_display = ("id", "patient", "doctor", "created_at")
    search_fields = ("patient__name", "doctor__name")

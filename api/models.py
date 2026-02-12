from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class TimeStampedModel(models.Model):
    """Small reusable base model to keep created/updated timestamps consistent."""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Patient(TimeStampedModel):
    class Gender(models.TextChoices):
        MALE = "male", "Male"
        FEMALE = "female", "Female"
        OTHER = "other", "Other"

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="patients")
    name = models.CharField(max_length=120)
    age = models.PositiveIntegerField()
    gender = models.CharField(max_length=10, choices=Gender.choices)
    address = models.TextField(blank=True)

    def __str__(self) -> str:
        return f"{self.name} ({self.age})"


class Doctor(TimeStampedModel):
    name = models.CharField(max_length=120)
    specialization = models.CharField(max_length=120)

    def __str__(self):
        return f"Dr. {self.name} - {self.specialization}"


class PatientDoctorMapping(TimeStampedModel):
    patient = models.ForeignKey(Patient, on_delete=models.PROTECT, related_name="mappings")
    doctor = models.ForeignKey(Doctor, on_delete=models.PROTECT, related_name="mappings")

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["patient", "doctor"], name="uniq_patient_doctor")
        ]

    def __str__(self):
        return f"Patient {self.patient_id} -> Doctor {self.doctor_id}"

from rest_framework import generics, viewsets, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.views import TokenObtainPairView
from django.shortcuts import get_object_or_404
from django.db.models import ProtectedError
from .models import Patient, Doctor, PatientDoctorMapping
from .serializers import (
    RegisterSerializer,
    EmailTokenObtainPairSerializer,
    PatientSerializer,
    DoctorSerializer,
    PatientDoctorMappingSerializer,
)


class RegisterView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer


class LoginView(TokenObtainPairView):
    permission_classes = [AllowAny]
    serializer_class = EmailTokenObtainPairSerializer


class PatientViewSet(viewsets.ModelViewSet):
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Patient.objects.filter(owner=self.request.user).order_by("-created_at")

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def perform_destroy(self, instance):
        try:
            instance.delete()
        except ProtectedError:
            raise ValidationError({
                "error": "Cannot delete patient. Please delete all associated patient-doctor mappings first."
            })


class DoctorViewSet(viewsets.ModelViewSet):
    serializer_class = DoctorSerializer
    permission_classes = [IsAuthenticated]
    queryset = Doctor.objects.all().order_by("-created_at")

    def perform_destroy(self, instance):
        try:
            instance.delete()
        except ProtectedError:
            raise ValidationError({
                "error": "Cannot delete doctor. Please delete all associated patient-doctor mappings first."
            })


class MappingListCreateView(generics.ListCreateAPIView):
    serializer_class = PatientDoctorMappingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Show mappings only for the user's patients
        return (
            PatientDoctorMapping.objects
            .filter(patient__owner=self.request.user)
            .select_related("patient", "doctor")
            .order_by("-created_at")
        )


class MappingDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id: int):
        patient = get_object_or_404(Patient, id=id, owner=request.user)
        doctors = Doctor.objects.filter(mappings__patient=patient).distinct()
        return Response(DoctorSerializer(doctors, many=True).data)

    def delete(self, request, id: int):
        mapping = get_object_or_404(PatientDoctorMapping, id=id, patient__owner=request.user)
        mapping.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

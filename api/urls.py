from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    RegisterView,
    LoginView,
    PatientViewSet,
    DoctorViewSet,
    MappingListCreateView,
    MappingDetailView,
)

router = DefaultRouter()
router.register(r"patients", PatientViewSet, basename="patients")
router.register(r"doctors", DoctorViewSet, basename="doctors")

urlpatterns = [
    # Auth
    path("auth/register/", RegisterView.as_view(), name="register"),
    path("auth/login/", LoginView.as_view(), name="login"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    # Mappings
    path("mappings/", MappingListCreateView.as_view(), name="mappings"),
    path("mappings/<int:id>/", MappingDetailView.as_view(), name="mapping_detail"),

    # Patients + Doctors
    path("", include(router.urls)),
]

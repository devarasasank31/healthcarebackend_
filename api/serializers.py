from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import Patient, Doctor, PatientDoctorMapping

User = get_user_model()


class RegisterSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)

    def validate_email(self, value: str) -> str:
        # We store email in username for simplicity, so username uniqueness gives us unique emails.
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["email"],
            email=validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data["name"],
        )
        return user

    def to_representation(self, instance):
        # Keep response small + clean
        return {
            "id": instance.id,
            "name": instance.first_name,
            "email": instance.email,
        }


class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    """SimpleJWT serializer that accepts {email, password} instead of {username, password}."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Replace username with email in the request body
        self.fields["email"] = serializers.EmailField()
        self.fields["password"] = serializers.CharField(write_only=True)

        self.fields.pop("username", None)

    def validate(self, attrs):
        # Map email -> username (we store username=email)
        email = attrs.get("email")
        password = attrs.get("password")
        return super().validate({"username": email, "password": password})

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Helpful (optional) claims
        token["email"] = user.email
        token["name"] = user.first_name
        return token


class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = ["id", "name", "age", "gender", "address", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class DoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = ["id", "name", "specialization", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class PatientDoctorMappingSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatientDoctorMapping
        fields = ["id", "patient", "doctor", "created_at"]
        read_only_fields = ["id", "created_at"]

    def validate_patient(self, patient):
        request = self.context.get("request")
        if request and patient.owner_id != request.user.id:
            raise serializers.ValidationError("You can only assign doctors to your own patients.")
        return patient

    def validate(self, attrs):
        patient = attrs.get("patient")
        doctor = attrs.get("doctor")

        if patient and doctor:
            if PatientDoctorMapping.objects.filter(patient=patient, doctor=doctor).exists():
                raise serializers.ValidationError("This doctor is already assigned to this patient.")
        return attrs

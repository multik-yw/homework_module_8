from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.generics import (
    CreateAPIView,
    DestroyAPIView,
    ListAPIView,
    RetrieveUpdateAPIView,
)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from users.models import Payment, User
from users.permissions import IsOwner
from users.serializers import PaymentSerializer, UserProfileSerializer, UserSerializer


# Create your views here.
class PaymentViewSet(ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ("payment_date", "paid_course", "paid_lesson", "payment_method")
    ordering_fields = ("payment_date",)
    ordering = ("-payment_date",)

    def get_queryset(self):
        if not self.request.user.is_staff:
            return Payment.objects.filter(user=self.request.user)
        return super().get_queryset()


class UserCreateAPIView(CreateAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = (AllowAny,)

    def perform_create(self, serializer):
        password = serializer.validated_data.get("password")
        user = serializer.save(is_active=True)
        if password:
            user.set_password(password)
            user.save()


class UserProfileAPIView(RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated, IsOwner]
    filter_backends = (filters.SearchFilter,)
    search_fields = (
        "email",
        "phone",
        "city",
    )
    queryset = User.objects.all()

    def get_object(self):
        if "pk" in self.kwargs:
            return super().get_object()
        return self.request.user

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class UserDeleteAPIView(DestroyAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsOwner]

    def get_object(self):
        return self.request.user


class UserListAPIView(ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [
        IsAuthenticated,
    ]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = {
        "email": ["exact"],
        "phone": ["exact"],
        "city": ["exact"],
        "is_active": ["exact"],
    }
    search_fields = ["email", "phone", "city"]
    ordering_fields = ["email", "date_joined"]
    ordering = ["-date_joined"]

    def get_queryset(self):
        if (
            self.request.user.is_staff
            or self.request.user.groups.filter(name="moders").exists()
        ):
            return User.objects.all()
        return User.objects.filter(id=self.request.user.id)

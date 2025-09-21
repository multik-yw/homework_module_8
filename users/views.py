from django.urls import reverse
from rest_framework import status
from drf_yasg import openapi
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

from materials.models import Course
from users.models import Payment, User
from users.serializers import PaymentSerializer, UserSerializer, UserProfileSerializer
from rest_framework.generics import (
    CreateAPIView,
    RetrieveUpdateAPIView,
    DestroyAPIView,
    ListAPIView,
)
from users.permissions import IsOwner
from drf_yasg.utils import swagger_auto_schema

from users.services import (
    create_stripe_product,
    create_stripe_price,
    create_stripe_session,
)

# flake8: noqa F841


# Create your views here.
class PaymentViewSet(ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ("payment_date", "paid_course", "paid_lesson", "payment_method")
    ordering_fields = ("payment_date",)
    ordering = ("-payment_date",)

    @swagger_auto_schema(
        operation_summary="Список платежей",
        operation_description="Список платежей",
        tags=["Платежи"],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Детали платежа",
        operation_description="Детали платежа",
        tags=["Платежи"],
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    def get_queryset(self):
        if not self.request.user.is_staff:
            return Payment.objects.filter(user=self.request.user)
        return super().get_queryset()


class UserCreateAPIView(CreateAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = (AllowAny,)

    @swagger_auto_schema(
        operation_summary="Регистрация пользователя",
        operation_description="Создание нового пользователя.",
        tags=["Пользователи"],
        responses={201: UserSerializer, 400: "Неверные данные"},
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

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

    @swagger_auto_schema(
        operation_summary="Получение профиля",
        operation_description="Получение профиля пользователя",
        tags=["Пользователи"],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Обновление профиля",
        operation_description="Обновление профиля пользователя",
        tags=["Пользователи"],
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Обновление профиля",
        operation_description="Обновление профиля пользователя",
        tags=["Пользователи"],
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

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

    @swagger_auto_schema(
        operation_summary="Удаление пользователя",
        operation_description="Удаление текущего пользователя",
        tags=["Пользователи"],
        responses={204: "No Content", 403: "Forbidden"},
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)

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

    @swagger_auto_schema(
        operation_summary="Список пользователей",
        operation_description="Список пользователей",
        tags=["Пользователи"],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        if (
            self.request.user.is_staff
            or self.request.user.groups.filter(name="moders").exists()
        ):
            return User.objects.all()
        return User.objects.filter(id=self.request.user.id)


class CoursePaymentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Оплата курса",
        operation_description="Создает платежную сессию Stripe для оплаты курса.",
        tags=["Платежи"],
        responses={
            200: openapi.Response(
                description="Ссылка на оплату",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "payment_link": openapi.Schema(type=openapi.TYPE_STRING)
                    },
                ),
            ),
            404: "Курс не найден",
        },
    )
    def post(self, request, course_id):
        course = get_object_or_404(Course, id=course_id)
        user = request.user

        product_id = create_stripe_product(course)
        price_id = create_stripe_price(product_id, course.price)

        success_url = request.build_absolute_uri(reverse("users:payment-success"))
        cancel_url = request.build_absolute_uri(reverse("users:payment-cancel"))
        session_data = create_stripe_session(price_id, success_url, cancel_url)

        payment = Payment.objects.create(
            user=user,
            paid_course=course,
            amount=course.price,
            payment_method="card",
            stripe_product_id=product_id,
            stripe_price_id=price_id,
            stripe_session_id=session_data["session_id"],
            stripe_payment_link=session_data["payment_link"],
        )

        return Response(
            {"payment_link": session_data["payment_link"]}, status=status.HTTP_200_OK
        )

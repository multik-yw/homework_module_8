from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import (
    CreateAPIView,
    ListAPIView,
    RetrieveAPIView,
    UpdateAPIView,
    DestroyAPIView,
)
from materials.models import Course, Lesson, Subscription
from materials.paginators import CustomPagination
from materials.serializers import (
    CourseSerializer,
    LessonSerializer,
    CourseDetailSerializer,
)
from drf_yasg import openapi
from users.permissions import IsModer, IsOwner
from drf_yasg.utils import swagger_auto_schema


# Create your views here.
class CourseViewSet(ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    pagination_class = CustomPagination

    @swagger_auto_schema(
        operation_summary="Создание курса",
        operation_description="Создание нового курса. Недоступно модераторам.",
        tags=["Курсы"],
        responses={
            201: CourseSerializer,
            403: "Forbidden (если пользователь — модератор)",
        },
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Обновление курса",
        operation_description="Обновление курса. Доступно владельцу или модератору.",
        tags=["Курсы"],
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Частичное обновление курса",
        operation_description="Частичное обновление курса. Доступно владельцу или модератору.",
        tags=["Курсы"],
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Удаление курса",
        operation_description="Удаление курса. Доступно только владельцу (не модератору).",
        tags=["Курсы"],
        responses={204: "No Content", 403: "Forbidden (если пользователь — модератор)"},
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    def get_serializer_class(self):
        if self.action == "retrieve":
            return CourseDetailSerializer
        return CourseSerializer

    def perform_create(self, serializer):
        course = serializer.save()
        course.owner = self.request.user
        course.save()

    def get_permissions(self):
        if self.action == "create":
            self.permission_classes = (~IsModer,)
        elif self.action == "retrieve":
            self.permission_classes = (IsAuthenticated,)
        elif self.action == "update":
            self.permission_classes = (IsModer | IsOwner,)
        elif self.action == "destroy":
            self.permission_classes = (IsOwner | ~IsModer,)
        return super().get_permissions()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context


class LessonCreateApiView(CreateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = (
        IsAuthenticated,
        ~IsModer,
    )

    @swagger_auto_schema(
        operation_summary="Создание урока",
        operation_description="Создание нового урока. Доступно только владельцам курсов (не модераторам).",
        tags=["Уроки"],
        responses={
            201: LessonSerializer,
            403: "Forbidden (если пользователь — модератор)",
        },
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class LessonListApiView(ListAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = CustomPagination


class LessonRetrieveApiView(RetrieveAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = (
        IsAuthenticated,
        IsModer | IsOwner,
    )

    @swagger_auto_schema(
        operation_summary="Детали урока",
        operation_description="Возвращает детали урока. Доступно владельцу или модератору.",
        tags=["Уроки"],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class LessonUpdateApiView(UpdateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = (
        IsAuthenticated,
        IsModer | IsOwner,
    )

    @swagger_auto_schema(
        operation_summary="Обновление урока",
        operation_description="Обновление урока. Доступно владельцу или модератору.",
        tags=["Уроки"],
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Полное обновление урока",
        operation_description="Полное обновление урока. Доступно владельцу или модератору.",
        tags=["Уроки"],
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)


class LessonDestroyApiView(DestroyAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = (
        IsAuthenticated,
        IsOwner | ~IsModer,
    )

    @swagger_auto_schema(
        operation_summary="Удаление урока",
        operation_description="Удаление урока. Доступно только владельцу (не модератору).",
        tags=["Уроки"],
        responses={204: "No Content", 403: "Forbidden (если пользователь — модератор)"},
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


class SubscriptionAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Подписка/отписка на курс",
        operation_description="Добавляет или удаляет подписку пользователя на курс.",
        tags=["Подписки"],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "course_id": openapi.Schema(
                    type=openapi.TYPE_INTEGER, description="ID курса"
                )
            },
            required=["course_id"],
        ),
        responses={
            200: openapi.Response(
                description="Успешная операция",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={"message": openapi.Schema(type=openapi.TYPE_STRING)},
                ),
            ),
            404: "Курс не найден",
        },
    )
    def post(self, request, *args, **kwargs):
        user = request.user
        course_id = request.data.get("course_id")
        course = get_object_or_404(Course, id=course_id)
        subscription, created = Subscription.objects.get_or_create(
            user=user, course=course
        )
        if not created:
            subscription.delete()
            message = "Подписка удалена"
        else:
            message = "Подписка добавлена"
        return Response({"message": message}, status=status.HTTP_200_OK)
from django.urls import path
from rest_framework.routers import SimpleRouter
from materials.apps import MaterialsConfig
from materials.views import (
    CourseViewSet,
    LessonCreateApiView,
    LessonUpdateApiView,
    LessonDestroyApiView,
    LessonListApiView,
    LessonRetrieveApiView,
    SubscriptionAPIView,
)
from drf_yasg.utils import swagger_auto_schema

app_name = MaterialsConfig.name

router = SimpleRouter()
router.register("", CourseViewSet)

lesson_list = swagger_auto_schema(
    method="get",
    operation_summary="Список уроков",
    operation_description="Возвращает paginated-список всех уроков.",
    tags=["Уроки"],
)(LessonListApiView.as_view())

urlpatterns = [
    path("lessons/", lesson_list, name="lessons_list"),
    path("lessons/<int:pk>/", LessonRetrieveApiView.as_view(), name="lesson_retrieve"),
    path("lessons/create/", LessonCreateApiView.as_view(), name="lesson_create"),
    path(
        "lessons/<int:pk>/delete/", LessonDestroyApiView.as_view(), name="lesson_delete"
    ),
    path(
        "lessons/<int:pk>/update/", LessonUpdateApiView.as_view(), name="lesson_update"
    ),
    path("subscriptions/", SubscriptionAPIView.as_view(), name="subscriptions"),
]

urlpatterns += router.urls
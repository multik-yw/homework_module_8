from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import ModelSerializer

from materials.models import Course, Lesson, Subscription
from materials.validators import YoutubeValidators


class CourseSerializer(ModelSerializer):
    count_lessons_in_course = SerializerMethodField()
    lessons = SerializerMethodField()
    is_subscribed = SerializerMethodField()

    class Meta:
        model = Course
        fields = "__all__"

    def get_count_lessons_in_course(self, course):
        return course.lesson_set.count()

    def get_lessons(self, course):
        lessons = course.lesson_set.all()
        return LessonSerializer(lessons, many=True).data

    def get_is_subscribed(self, obj):
        user = self.context["request"].user
        if user.is_authenticated:
            return obj.subscriptions.filter(user=user).exists()
        return False


class CourseDetailSerializer(ModelSerializer):
    count_lessons_in_course = SerializerMethodField()
    lessons = SerializerMethodField()
    is_subscribed = SerializerMethodField()

    def get_count_lessons_in_course(self, course):
        return course.lesson_set.count()

    def get_lessons(self, course):
        lessons = course.lesson_set.all()
        return LessonSerializer(lessons, many=True).data

    def get_is_subscribed(self, obj):
        user = self.context["request"].user
        if user.is_authenticated:
            return obj.subscriptions.filter(user=user).exists()
        return False

    class Meta:
        model = Course
        fields = (
            "name",
            "count_lessons_in_course",
            "lessons",
            "is_subscribed",
        )

class LessonSerializer(ModelSerializer):
    class Meta:
        model = Lesson
        fields = '__all__'
        extra_kwargs = {"video_link": {"validators": [YoutubeValidators]}}

class SubscriptionSerializer(ModelSerializer):
    class Meta:
        model = Subscription
        fields = "__all__"
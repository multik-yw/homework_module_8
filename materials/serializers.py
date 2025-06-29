from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import ModelSerializer
from materials.models import Course, Lesson


class CourseSerializer(ModelSerializer):
    count_lessons_in_course = SerializerMethodField()
    lessons = SerializerMethodField()

    class Meta:
        model = Course
        fields = '__all__'

    def get_count_lessons_in_course(self, course):
        return course.lesson_set.count()

    def get_lessons(self, course):
        lessons = course.lesson_set.all()
        return LessonSerializer(lessons, many=True).data


class CourseDetailSerializer(ModelSerializer):
    count_lessons_in_course = SerializerMethodField()
    lessons = SerializerMethodField()

    def get_count_lessons_in_course(self, course):
        return course.lesson_set.count()

    def get_lessons(self, course):
        lessons = course.lesson_set.all()
        return LessonSerializer(lessons, many=True).data

    class Meta:
        model = Course
        fields = ('name', "count_lessons_in_course", 'lessons',)

class LessonSerializer(ModelSerializer):
    class Meta:
        model = Lesson
        fields = '__all__'
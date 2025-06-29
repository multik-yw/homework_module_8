from django.core.management.base import BaseCommand
from users.models import Payment
from materials.models import Course, Lesson
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Заполнение таблицы Payments'

    def handle(self, *args, **options):
        User.objects.all().delete()
        Lesson.objects.all().delete()
        Course.objects.all().delete()
        Payment.objects.all().delete()


        user1 = User.objects.create(email='test1@example.com',)

        user2 = User.objects.create(email='test2@example.com',)


        course1 = Course.objects.create(name='Тестовый курс 1',)

        course2 = Course.objects.create( name='Тестовый курс 2',)


        lesson1 = Lesson.objects.create(name='Тестовый урок 1', course=course1)

        lesson2 = Lesson.objects.create(name='Тестовый урок 2', course=course1)

        lesson3 = Lesson.objects.create(name='Тестовый урок 3', course=course2)

        payment_data = [
            {
                'user': user1,
                'paid_course': course1,
                'paid_lesson': None,
                'amount': 100,
                'payment_method': 'cash',
                'payment_date': '2025-01-01'
            },
            {
                'user': user1,
                'paid_course': None,
                'paid_lesson': lesson2,
                'amount': 200,
                'payment_method': 'transfer',
                'payment_date': "2025-01-02"
            },
            {
                'user': user2,
                'paid_course': course2,
                'paid_lesson': None,
                'amount': 300,
                'payment_method': 'transfer',
                'payment_date': "2025-01-03"
            },
            {
                'user': user2,
                'paid_course': None,
                'paid_lesson': lesson3,
                'amount': 400,
                'payment_method': 'cash',
                'payment_date': "2025-01-04"
            }
        ]

        for data in payment_data:
            Payment.objects.create(**data)

        self.stdout.write(self.style.SUCCESS('Данные созданы'))
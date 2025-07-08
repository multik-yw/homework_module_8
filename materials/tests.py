from django.contrib.auth.models import Group
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from materials.models import Course, Lesson, Subscription
from users.models import User


class LessonCRUDTestCase(APITestCase):
    def setUp(self):
        self.moder_group = Group.objects.create(name="moders")

        self.owner = User.objects.create(email="owner1@test.com", password="testpass")
        self.moderator = User.objects.create(
            email="moderator1@test.com", password="testpass"
        )
        self.moderator.groups.add(self.moder_group)
        self.other_user = User.objects.create(
            email="other1@test.com", password="testpass"
        )

        self.course = Course.objects.create(name="Test Course", owner=self.owner)
        self.lesson = Lesson.objects.create(
            name="Test Lesson",
            course=self.course,
            video_link="https://youtube.com/test",
            owner=self.owner,
        )

        self.lesson_list_url = reverse("materials:lessons_list")
        self.lesson_detail_url = reverse(
            "materials:lesson_retrieve", kwargs={"pk": self.lesson.pk}
        )

    def test_lesson_create_owner(self):
        self.client.force_authenticate(user=self.owner)
        data = {
            "name": "New Lesson",
            "course": self.course.pk,
            "video_link": "https://youtube.com/new",
        }
        response = self.client.post(reverse("materials:lesson_create"), data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Lesson.objects.count(), 2)

    def test_lesson_create_moderator(self):
        self.client.force_authenticate(user=self.moderator)
        data = {
            "name": "New Lesson",
            "course": self.course.pk,
            "video_link": "https://youtube.com/new",
        }
        response = self.client.post(reverse("materials:lesson_create"), data=data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_lesson_delete(self):
        self.client.force_authenticate(user=self.other_user)
        response = self.client.delete(
            reverse("materials:lesson_delete", kwargs={"pk": self.lesson.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class SubscriptionTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(email="user@test.com", password="testpass")
        self.course = Course.objects.create(name="Test Course")
        self.subscription_url = reverse("materials:subscriptions")

    def test_subscription_create_and_delete(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            self.subscription_url, data={"course_id": self.course.pk}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Подписка добавлена")
        self.assertTrue(
            Subscription.objects.filter(user=self.user, course=self.course).exists()
        )

        response = self.client.post(
            self.subscription_url, data={"course_id": self.course.pk}
        )
        self.assertEqual(response.data["message"], "Подписка удалена")
        self.assertFalse(
            Subscription.objects.filter(user=self.user, course=self.course).exists()
        )

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from materials.models import Course, Lesson, Subscription
from users.models import User

class CourseTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='testuser@example.com', password='testpass')
        self.client.login(email='testuser@example.com', password='testpass')
        self.course = Course.objects.create(name='Test Course', owner=self.user)

    def test_create_course(self):
        url = reverse('materials:course-list')
        data = {
            'name': 'New Course',
            'description': 'Description of the new course',
            'preview': None
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Course.objects.count(), 2)

    def test_list_courses(self):
        url = reverse('materials:course-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_course_detail(self):
        url = reverse('materials:course-detail', args=[self.course.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.course.name)

class LessonTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='testuser@example.com', password='testpass')
        self.client.login(email='testuser@example.com', password='testpass')
        self.course = Course.objects.create(name='Test Course', owner=self.user)
        self.lesson = Lesson.objects.create(
            name='Test Lesson',
            course=self.course,
            owner=self.user,
            video_link='https://www.youtube.com/watch?v=test'
        )

    def test_create_lesson(self):
        url = reverse('materials:lesson_create')
        data = {
            'name': 'New Lesson',
            'description': 'Description of the new lesson',
            'video_link': 'https://www.youtube.com/watch?v=newlesson',
            'course': self.course.id,
            'preview': None
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Lesson.objects.count(), 2)

    def test_list_lessons(self):
        url = reverse('materials:lessons_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_lesson_detail(self):
        url = reverse('materials:lesson_retrieve', args=[self.lesson.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.lesson.name)

class SubscriptionTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='testuser@example.com', password='testpass')
        self.client.login(email='testuser@example.com', password='testpass')
        self.course = Course.objects.create(name='Test Course', owner=self.user)

    def test_subscribe_to_course(self):
        url = reverse('materials:subscriptions')
        data = {'course_id': self.course.id}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(Subscription.objects.filter(user=self.user, course=self.course).exists())

    def test_unsubscribe_from_course(self):
        Subscription.objects.create(user=self.user, course=self.course)
        url = reverse('materials:subscriptions')
        data = {'course_id': self.course.id}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Subscription.objects.filter(user=self.user, course=self.course).exists())


class UserTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='testuser@example.com', password='testpass')

    def test_register_user(self):
        url = reverse('users:register')
        data = {
            'email': 'newuser@example.com',
            'password': 'newpassword',
            'phone': '1234567890',
            'city': 'Test City',
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email='newuser@example.com').exists())

    def test_login_user(self):
        url = reverse('users:token_obtain_pair')
        data = {
            'email': 'testuser@example.com',
            'password': 'testpass'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_get_user_profile(self):
        self.client.login(email='testuser@example.com', password='testpass')
        url = reverse('users:profile-current')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], self.user.email)

    def test_update_user_profile(self):
        self.client.login(email='testuser@example.com', password='testpass')
        url = reverse('users:profile-current')
        data = {
            'phone': '123456789',
            'city': 'Updated City'
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.phone, '123456789')
        self.assertEqual(self.user.city, 'Updated City')

    def test_delete_user_profile(self):
        self.client.login(email='testuser@example.com', password='testpass')
        url = reverse('users:profile-delete')
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.filter(email='testuser@example.com').exists())
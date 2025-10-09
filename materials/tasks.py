from django.core.mail import send_mail
from celery import shared_task
from config import settings
from materials.models import Course, Subscription
import logging

logger = logging.getLogger(__name__)


@shared_task
def send_course_update_notification(course_id):
    try:
        course = Course.objects.get(id=course_id)
        subscribers_emails = Subscription.objects.filter(course=course).values_list(
            "user__email", flat=True
        )

        if not subscribers_emails:
            return "Нет подписчиков для рассылки"

        send_mail(
            subject=f"Обновление курса: {course.name}",
            message=f"Курс '{course.name}' был обновлен",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=list(subscribers_emails),
            fail_silently=False,
        )
        return f"Уведомления отправлены {len(subscribers_emails)} подписчикам"
    except Exception as e:
        logger.error(f"Ошибка: {str(e)}")
        return f"Ошибка при отправке: {str(e)}"

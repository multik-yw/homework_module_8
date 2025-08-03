from celery import shared_task
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


@shared_task
def check_inactive_users():
    """Проверяет пользователей, которые не заходили больше месяца, и деактивирует их."""
    try:
        one_month_ago = timezone.now() - timedelta(days=30)
        inactive_users = User.objects.filter(
            last_login__lt=one_month_ago, is_active=True
        )

        count = inactive_users.count()
        inactive_users.update(is_active=False)

        logger.info(f"Заблокировано {count} неактивных пользователей.")
        return f"Заблокировано {count} пользователей."

    except Exception as e:
        logger.error(f"Ошибка: {str(e)}")
        return f"Ошибка: {str(e)}"

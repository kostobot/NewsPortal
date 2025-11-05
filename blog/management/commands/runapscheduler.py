import logging

from django.conf import settings

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.core.management.base import BaseCommand
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution

from django.core.mail import send_mail
from django.contrib.auth.models import User
from ...models import Post
from datetime import timedelta
from django.utils import timezone


logger = logging.getLogger(__name__)


def my_job():
    now = timezone.now()
    list_week_posts = Post.objects.filter(date_time__gte=now - timedelta(days=7))

    for user in User.objects.filter():
        list_category_id = list(user.categories.values_list('id', flat=True))
        list_week_posts_user = list_week_posts.filter(category__in=list_category_id)

        if list_week_posts_user:
            list_posts = ''
            for post in list_week_posts_user:
                list_posts += f'\n{post.title}\nhttp://127.0.0.1:8000/posts/{post.id}'

            send_mail(
                subject=f'News Portal: посты за прошедшую неделю.',
                message=f'Доброго дня, {user.username}!\nПредлагаем Вам ознакомиться с новыми постами, появившимися за последние 7 дней:\n{list_posts}',
                from_email='kastetpsy@yandex.ru',
                recipient_list=[user.email],
            )


def delete_old_job_executions(max_age=604_800):
    """This job deletes all apscheduler job executions older than `max_age` from the database."""
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


class Command(BaseCommand):
    help = "Runs apscheduler."

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        scheduler.add_job(
            my_job,
            trigger=CronTrigger(
                day_of_week="tue",
                hour="14",
                minute="00",
            ),
            id="my_job",
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added job 'my_job'.")

        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(
                day_of_week="tue", hour="14", minute="00"
            ),
            id="delete_old_job_executions",
            max_instances=1,
            replace_existing=True,
        )
        logger.info(
            "Added weekly job: 'delete_old_job_executions'."
        )

        try:
            logger.info("Starting scheduler...")
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Stopping scheduler...")
            scheduler.shutdown()
            logger.info("Scheduler shut down successfully!")
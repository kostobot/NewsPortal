# Итоговое задание 5.4 (HW-03)

## Отчёт о реализации функционала рассылок и уведомлений в приложении NewsPortal.

### Задание 1. В категории должна быть возможность пользователей подписываться на рассылку новых статей в этой категории.

**Описание реализации:**
В приложении реализован механизм подписки на категории новостей.
Пользователь может выбрать интересующую его категорию и оформить подписку, после чего будет получать уведомления о новых новостях/статьях в этой категории.

**Список категорий доступен по адресу:** http://127.0.0.1:8000/posts/categories/

**Функционал:**
При выборе категории пользователь переходит на страницу новсотей/статей конкретной категории, где доступна кнопка «Подписаться».

После нажатия на кнопку пользователю отправляется email-уведомление о том, что подписка успешно оформлена.

**Ключевой код (`views.py`):**
```python
@login_required 
def add_subscribe(request, pk):
    user = request.user
    category = get_object_or_404(Category, pk=pk)
    category.subscribers.add(request.user)
    
    text_content = f'Здравствуй, {user.username} ! Вы подписались на категорию "{category.name}". '
    f'Теперь вы будете одним из первых узнавать о новостях из этой категории!'
    html_content = render_to_string('add_subscribe.html', {'username': user.username, 'category': category.name})
    
    msg = EmailMultiAlternatives(
        subject=f'News Portal: {category.name}',
        body=text_content,
        from_email='News Portal <kastetpsy@yandex.ru>',
        to=[user.email],
    )
    msg.attach_alternative(html_content, "text/html")
    msg.send()
    
    return redirect('category_posts', pk=pk)
```

**Результат:**
После подписки пользователь получает письмо с подтверждением подписки на выбранную категорию и уведомлением о предстоящих рассылках.


### Задание 2. Если пользователь подписан на какую-либо категорию, то, как только в неё добавляется новая статья, её краткое содержание приходит пользователю на электронную почту, которую он указал при регистрации. В письме обязательно должна быть гиперссылка на саму статью, чтобы он мог по клику перейти и прочитать её.

**Описание реализации:**
Функционал реализован с использованием механизма сигналов Django.
Сигнал m2m_changed отслеживает добавление новой статьи (Post) в категорию (Category).
При возникновении события система формирует и отправляет письма всем подписчикам категории.

**Ключевой код (signals.py):**
```python
@receiver(m2m_changed, sender=Post.category.through)
def notify_users_new_post(sender, instance, action, **kwargs):
    if action == 'post_add':
        categories = instance.category.all()

        for category in categories:
            subscribers = category.subscribers.all()

            for user in subscribers:
                if not user.email:
                    continue

                subject = f'Новый пост в категории: {category.name}'

                preview_text = instance.text[:50] + ('...' if len(instance.text) > 50 else '')

                text_content = f'Здравствуй, {user.username}!\nНовая статья в твоём любимом разделе {instance.title}\n\n{preview_text} !'

                html_content = render_to_string('subscribe_new_post.html', {'post': instance, 'username': user.username, 'category': category.name})

                email = EmailMultiAlternatives(
                    subject=subject,
                    body=text_content,
                    from_email='kastetpsy@yandex.ru',
                    to=[user.email],
                )
                email.attach_alternative(html_content, "text/html")
                email.send()
```

**Результат:**
Каждый раз при публикации новой статьи подписчики категории автоматически получают письмо с кратким описанием поста и гиперссылкой для перехода к полной версии.

### Задание 3. Если пользователь подписан на какую-либо категорию, то каждую неделю ему приходит на почту список новых статей, появившийся за неделю с гиперссылкой на них, чтобы пользователь мог перейти и прочесть любую из статей.

**Описание реализации:**
Функционал реализован с использованием планировщика APScheduler, интегрированного с Django.
Задача выполняется еженедельно во вторник в 14:00.
Система формирует список постов, опубликованных за неделю, и рассылает его пользователям, подписанным на соответствующие категории.

**Ключевой код (runapscheduler.py):**
```python
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
    """Удаляет из базы данных старые записи о выполненных задачах APScheduler."""
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
        logger.info("Added weekly job: 'delete_old_job_executions'.")

        try:
            logger.info("Starting scheduler...")
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Stopping scheduler...")
            scheduler.shutdown()
            logger.info("Scheduler shut down successfully!")
```

**Результат:**
Каждую неделю пользователи получают на email письмо с подборкой новых статей, опубликованных в интересующих их категориях, с гиперссылками на каждую публикацию.

**Запуск планировщика:**
python manage.py runapscheduler

### Задание 4. Добавьте приветственное письмо пользователю при регистрации в приложении.

**Описание реализации:**
Сигналы email_confirmed (для стандартной регистрации) и user_signed_up (для регистрации через социальные сети) отслеживают успешное завершение процесса регистрации.
После этого пользователю отправляется приветственное письмо.

**Ключевой код (signals.py):**
```python
def _send_welcome_email(user):
    send_mail(
        subject='Добро пожаловать!',
        message=f'Привет, {user.username}!\n\n'
                f'Рады видеть вас в нашем приложении 🎉\n'
                f'Выбирайте любимые категории новостей и первыми узнавайте о самых свежих публикациях прямо на почте.\n\n'
                f'Спасибо, что с нами!\nВаша команда NewsPortal',
        from_email='kastetpsy@yandex.ru',
        recipient_list=[user.email],
        fail_silently=False,
    )
    
@receiver(email_confirmed)
def welcome_email_after_register(request, email_address, **kwargs):
    user = email_address.user
    _send_welcome_email(user)
    
@receiver(user_signed_up)
def welcome_after_social_signup(request, user, **kwargs):
    sociallogin = kwargs.get('sociallogin')
    if sociallogin:
        _send_welcome_email(user)
```

**Результат:**
После регистрации или подтверждения email пользователь получает письмо с приветствием и краткой инструкцией по использованию портала.

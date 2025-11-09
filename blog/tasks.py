from celery import shared_task
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from .models import Post
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail
from django.contrib.auth.models import User


@shared_task
def send_new_post_notifications(post_id):
    post = Post.objects.get(pk=post_id)
    categories = post.category.all()

    for category in categories:
        subscribers = category.subscribers.all()

        for user in subscribers:
            if not user.email:
                continue

            subject = f'Новый пост в категории: {category.name}'
            preview_text = post.text[:50] + ('...' if len(post.text) > 50 else '')

            text_content = (
                f'Здравствуй, {user.username}!\n'
                f'Новая статья в твоём любимом разделе "{category.name}": {post.title}\n\n'
                f'{preview_text}'
            )

            html_content = render_to_string(
                'subscribe_new_post.html',
                {'post': post, 'username': user.username, 'category': category.name}
            )

            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email='kastetpsy@yandex.ru',
                to=[user.email],
            )
            email.attach_alternative(html_content, "text/html")
            email.send()

@shared_task
def send_weekly_digest():
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
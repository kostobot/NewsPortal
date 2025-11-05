from django.core.mail import EmailMultiAlternatives, send_mail
from django.dispatch import receiver
from django.db.models.signals import m2m_changed
from .models import Post, Author
from django.template.loader import render_to_string
from django.contrib.auth.models import User, Group
from allauth.account.signals import email_confirmed, user_signed_up


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


@receiver(m2m_changed, sender=User.groups.through)
def add_author_on_group_add(sender, instance, action, pk_set, **kwargs):
    if action == 'post_add':
        authors_group = Group.objects.filter(name='authors').first()
        if not authors_group:
            return
        if authors_group.pk in pk_set:
            if not hasattr(instance, 'author'):
                Author.objects.create(user=instance)

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
    

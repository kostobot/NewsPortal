from django.core.mail import EmailMultiAlternatives, send_mail
from django.dispatch import receiver, Signal
from django.db.models.signals import m2m_changed
from django.template.loader import render_to_string
from django.contrib.auth.models import User, Group
from allauth.account.signals import email_confirmed
from django.dispatch import receiver

user_registered = Signal()

@receiver(user_registered)
def send_welcome_email_after_register(sender, user, **kwargs):
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


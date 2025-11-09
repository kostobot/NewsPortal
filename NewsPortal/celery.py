import os
from celery import Celery
from celery.schedules import crontab
 
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'NewsPortal.settings')
 
app = Celery('NewsPortal')
app.config_from_object('django.conf:settings', namespace = 'CELERY')

app.autodiscover_tasks()

app.conf.beat_schedule = {
    'send-weekly-digest': {
        'task': 'blog.tasks.send_weekly_digest',
        'schedule': crontab(minute='05', hour='01')
        # 'schedule': crontab(minute='00', hour='08', day_of_week='monday')
    },
}
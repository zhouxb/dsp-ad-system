from celery import Celery
from app.core.config import settings
import os

def make_celery(app=None):
    """
    Create a Celery instance for handling async tasks
    
    Args:
        app: Flask app to bind Celery with
        
    Returns:
        Configured Celery instance
    """
    celery = Celery(
        app.import_name if app else 'dsp_ad_system',
        backend=settings.CELERY_RESULT_BACKEND,
        broker=settings.CELERY_BROKER_URL
    )
    
    # Configure Celery
    celery.conf.update(
        result_expires=3600,  # results expire in 1 hour
        worker_prefetch_multiplier=1,
        task_acks_late=True,
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',
        timezone='UTC',
        enable_utc=True,
    )
    
    # Configure periodic tasks if any
    celery.conf.beat_schedule = {
        'update-hourly-stats': {
            'task': 'app.tasks.report.update_hourly_stats',
            'schedule': 60.0,  # run every minute
        },
        'update-daily-stats': {
            'task': 'app.tasks.report.update_daily_stats',
            'schedule': 3600.0,  # run every hour
        },
    }
    
    # If app is provided, create a Flask app context for tasks
    if app:
        class FlaskTask(celery.Task):
            def __call__(self, *args, **kwargs):
                with app.app_context():
                    return self.run(*args, **kwargs)
        
        celery.Task = FlaskTask
    
    return celery 
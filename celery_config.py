""" Celery configuration"""

from celery import Celery
import configuration

config = configuration.Config()

broker_url = config.get_broker_url()
result_backend = config.celery.backend
task_serializer = "json"
result_serializer = "json"
accept_content = ["json"]
timezone = "UTC"
enable_utc = True
broker_connection_retry_on_startup = True

beat_schedule = {
    "upload_images_to_cloud": {
        "task": "features.images.tasks.upload_images_to_cloud_storage",
        "schedule": 600,  # Set the interval in seconds
    },
}
celery = Celery(
    __name__,
    broker=broker_url,
    backend=result_backend,
    task_serializer=task_serializer,
    result_serializer=result_serializer,
    accept_content=accept_content,
    timezone=timezone,
    enable_utc=enable_utc,
    broker_connection_retry_on_startup=broker_connection_retry_on_startup,
    include=["features.images.tasks"],
    beat_schedule=beat_schedule,
)

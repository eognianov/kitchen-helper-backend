""" Tasks related to image processing"""
from celery_config import celery
import time


@celery.task
def upload_images_to_cloud_storage():
    time.sleep(5)
    print("Scheduled task is running!")
    return "Task is complete!"

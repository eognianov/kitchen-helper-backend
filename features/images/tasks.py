""" Tasks related to image processing"""
import datetime
import os

import db.connection
import features.images.models
import khLogging
from celery_config import celery
from .operations import upload_image_to_cloud
from .helpers import read_image_as_bytes

logging = khLogging.Logger.get_child_logger(__file__)


@celery.task
def upload_images_to_cloud_storage():
    """
    Periodical celery task for uploading images to cloud storage
    After successful upload delete the image from local storage
    :return:
    """

    with db.connection.get_session() as session:
        images_to_upload = (
            session.query(features.images.models.Image)
            .filter(features.images.models.Image.in_cloudinary.is_(False))
            .all()
        )

        if not images_to_upload:
            return "No images to be uploaded to cloud!"

        uploaded_images = 0
        not_uploaded_images = 0

        for image in images_to_upload:
            try:
                content, image_path = read_image_as_bytes(image)
                success = upload_image_to_cloud(
                    content=content, image_name=image.name, uploader="me"
                )
                if success:
                    image.in_cloudinary = True
                    session.add(image)
                    session.commit()
                    session.refresh(image)
                    uploaded_images += 1

            except Exception as e:
                not_uploaded_images += 1
                logging.error(f"Error uploading image {image.name}: {str(e)}")

        session.close()

    logging.info(
        f"Total images: {not_uploaded_images + uploaded_images}"
        + os.linesep
        + f"Images uploaded to cloud: {uploaded_images}"
        + os.linesep
        + f"Not uploaded images: {not_uploaded_images}"
    )
    return

import fastapi

import common.authentication
import features.images.operations
from .responses import ImageResponse
from .exceptions import InvalidCreationInputException, ImageUrlIsNotReachable, ImageNotFoundException
import khLogging

router = fastapi.APIRouter()


logging = khLogging.Logger.get_child_logger('images')


@router.post('/', response_model=ImageResponse)
async def upload_image(user: common.authentication.authenticated_user, url: str = fastapi.Form(default=None), file: fastapi.UploadFile = fastapi.File(default=None)):
    """
    Upload image

    :param user:
    :param url:
    :param file:
    :return:
    """

    try:
        file_content = None
        if file:
            file_content = await file.read()

        return await features.images.operations.add_image(added_by=user.id, url=url, image=file_content)
    except InvalidCreationInputException:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_400_BAD_REQUEST,
            detail="You have to provide url or file!"
        )
    except ValueError as err:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_400_BAD_REQUEST,
            detail=f"Can not process the image! {err}"
        )
    except ImageUrlIsNotReachable:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_424_FAILED_DEPENDENCY,
            detail="Can not get image from the url!"
        )


@router.get('/{image_id}', response_model=ImageResponse)
async def get_image(image_id: int = fastapi.Path()):
    """
    Get image
    :param image_id:
    :return:
    """

    try:
        return await features.images.operations.get_image(image_id)
    except ImageNotFoundException:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_404_NOT_FOUND,
            detail=f"Image with id: {image_id} does not exist!"
        )


@router.get('/', response_model=list[ImageResponse])
async def get_images():
    """
    Get images
    :return:
    """

    return await features.images.operations.get_images()
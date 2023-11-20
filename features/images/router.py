import fastapi
from .operations import add_image
from .responses import ImageResponse
from .exceptions import InvalidCreationInputException, ImageUrlIsNotReachable
import khLogging

router = fastapi.APIRouter()


logging = khLogging.Logger.get_child_logger('images')


@router.post('/', response_model=ImageResponse)
async def upload_image(url: str = fastapi.Form(default=None), file: fastapi.UploadFile = fastapi.File(default=None)):
    """
    Upload image
    :param url:
    :param file:
    :return:
    """

    try:
        file_content = None
        if file:
            file_content = await file.read()

        return await add_image(url, file_content)
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

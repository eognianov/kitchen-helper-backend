from fastapi import APIRouter, UploadFile, HTTPException
from .operations import save_image_from_file, save_image_from_url
from .input_models import ImageFromUrl
from .responses import ImageResponse

router = APIRouter()


@router.post("/upload/file/", response_model=ImageResponse)
async def upload_image(file: UploadFile):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload an image.")

    try:
        static_uploader = "test_uploader"
        image_data = await save_image_from_file(file, static_uploader)
        return image_data
    except Exception as e:  # Todo
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/upload/url/")
async def upload_image_from_url(image_data: ImageFromUrl):
    try:
        static_uploader = "test_uploader"
        image_data = await save_image_from_url(image_data.url, static_uploader)
        return image_data
    except Exception as e:  # Todo
        raise HTTPException(status_code=400, detail=str(e))

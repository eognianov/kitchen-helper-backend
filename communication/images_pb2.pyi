from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class ImageRequest(_message.Message):
    __slots__ = ("image_id",)
    IMAGE_ID_FIELD_NUMBER: _ClassVar[int]
    image_id: int
    def __init__(self, image_id: _Optional[int] = ...) -> None: ...

class ImageResponse(_message.Message):
    __slots__ = ("image_url",)
    IMAGE_URL_FIELD_NUMBER: _ClassVar[int]
    image_url: str
    def __init__(self, image_url: _Optional[str] = ...) -> None: ...

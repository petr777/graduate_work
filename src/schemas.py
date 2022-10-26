import hashlib
import json
from enum import Enum
from pydantic import BaseModel
from typing import Union, Optional
from settings import settings


class Format(str, Enum):
    mpg = 'mpegts'
    mp4 = 'mp4'
    mov = 'mov'
    mkv = 'matroska'
    avi = 'avi'


class Vcodec(str, Enum):
    h264 = 'libx264'
    h265 = 'libx265'
    vp9 = 'libvpx-vp9'


class Size(str, Enum):
    sd = '720x480'
    hd = '1280x720'
    full_hd = '1920x1080'
    ultra_hd = '3840x2160'


class Acodec(str, Enum):
    mp3 = 'mp3'
    aac = 'aac'


class ConvertSchema(BaseModel):

    size: Optional[Size] = '1920x1080'
    vcodec: Optional[Vcodec] = 'libx264'
    acodec: Optional[Acodec] = 'aac'
    format: Optional[Format] = 'mp4'

    class Config:
        use_enum_values = True

    @classmethod
    def get_field_names(cls, alias=False):
        return list(cls.schema(alias).get("properties").keys())

    def get_hash(self):
        b_json = json.dumps(self.__dict__).encode('utf-8')
        hash_object = hashlib.md5(b_json)
        hex_dig = hash_object.hexdigest()
        return hex_dig


class ETLSchema(BaseModel):
    destination_folder: Optional[str]
    convert_schema: Union[ConvertSchema, None] = None
    bucket_out: str = settings.aws.bucket_hot


class MediaInfoSchema(BaseModel):
    duration: float
    size: str
    vcodec: str
    acodec: str
    format: str

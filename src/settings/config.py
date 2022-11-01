from pydantic import BaseSettings, validator, PostgresDsn, Field
from pathlib import Path
import os
from typing import Dict


BASE_DIR = Path(os.path.dirname(os.path.dirname(__file__)))


class Base(BaseSettings):

    class Config:
        env_file = os.path.join(BASE_DIR, '.env')


class SettingsAWS(Base):

    access_key_id: str
    secret_access_key: str
    endpoint_url: str = 'https://hb.bizmrg.com'

    bucket_ice: str = 'serverok_ice'
    bucket_hot: str = 'serverok_hot'

    dns: Dict = None

    @validator("dns", pre=True)
    def build_dsn(cls, v, values) -> dict:
        return {
            "aws_access_key_id": values["access_key_id"],
            "aws_secret_access_key": values["secret_access_key"],
            "endpoint_url": values["endpoint_url"]
        }

    class Config:
        env_prefix = "AWS_"


class SettingsPG(Base):
    protocol: str = "postgresql+asyncpg"
    user: str = ''
    password: str = ''
    host: str = '127.0.0.1'
    port: int = 5432
    pool_recycle: int = 1800
    pg_schema: str = "content"
    path: str = Field(..., env="POSTGRES_DB")
    dns: PostgresDsn = None

    @validator("dns", pre=True)
    def build_dsn(cls, v, values) -> str:
        protocol = values['protocol']
        user = values['user']
        password = values['password']
        host = values['host']
        port = values['port']
        path = values['path']

        return f"{protocol}://{user}:{password}@{host}:{port}/{path}"

    class Config:
        env_prefix = "POSTGRES_"


class Settings(Base):

    base_dir: Path = BASE_DIR
    temporary_dir: Path = BASE_DIR / 'serverok'
    batch_size: int = 3

    pg: SettingsPG = SettingsPG()
    aws: SettingsAWS = SettingsAWS()

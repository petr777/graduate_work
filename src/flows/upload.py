from aiovk import AioVK
from services.vk import MediaServiceVK
from uuid import uuid4
from prefect import task, get_run_logger
from pathlib import Path
import aiofiles


async def upload_file(
        convert_file: str,
        bucket_out: str,
        destination_folder: str) -> str:

    suffix = Path(convert_file).suffix
    name_file = str(uuid4())
    key = f'{destination_folder}/{name_file}{suffix}'

    async with aiofiles.open(convert_file, "rb") as out:
        content = await out.read()
        async with AioVK() as vk_client:
            media_service_vk = MediaServiceVK(vk_client)
            await media_service_vk.put_file(
                bucket=bucket_out,
                key=key,
                content=content
            )
            return key


@task(retries=3, retry_delay_seconds=10)
async def upload_task(
        convert_file: str,
        bucket_out: str,
        destination_folder: str) -> str:
    logger = get_run_logger()
    try:
        file = await upload_file(convert_file, bucket_out, destination_folder)
        return file
    except Exception as error:
        logger.error(error)

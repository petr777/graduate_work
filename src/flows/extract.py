from aiovk import AioVK
from services.vk import MediaServiceVK
from prefect import task, get_run_logger
from aiofiles.tempfile import NamedTemporaryFile
from pathlib import Path


async def extract_file(key: str, bucket: str) -> NamedTemporaryFile:
    suffix = Path(key).suffix
    async with AioVK() as vk_client:
        media_service_vk = MediaServiceVK(vk_client)
        content = await media_service_vk.get_file(bucket=bucket, key=key)

        async with NamedTemporaryFile(
                'wb', delete=False, suffix=suffix
        ) as temp_file:
            await temp_file.write(content)
            return temp_file


@task(retries=3, retry_delay_seconds=30)
async def extracted_task(file: str, bucket: str) -> NamedTemporaryFile:
    logger = get_run_logger()
    try:
        temp_file = await extract_file(file, bucket=bucket)
        return temp_file
    except Exception as error:
        logger.error(error)

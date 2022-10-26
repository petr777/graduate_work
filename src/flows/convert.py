import asyncio
from schemas import ConvertSchema
from prefect import task, get_run_logger
from aiofiles.tempfile import NamedTemporaryFile
from pathlib import Path


async def make_cmd(
        file_in: str,
        file_out: str,
        convert_schema: ConvertSchema) -> str:
    cmd = ['ffmpeg', '-i', file_in]

    if convert_schema.size:
        cmd.extend(['-s', convert_schema.size])
    if convert_schema.vcodec:
        cmd.extend(['-codec:v', convert_schema.vcodec])
    if convert_schema.acodec:
        cmd.extend(['-codec:a', convert_schema.acodec])

    cmd.extend(['-y', file_out])
    cmd = ' '.join(cmd)
    return cmd


async def get_blunk_file(suffix: str):
    async with NamedTemporaryFile(
            'wb', suffix=suffix, delete=False) as file_out:
        return file_out


async def convert_file(
        file_in: NamedTemporaryFile,
        convert_schema: ConvertSchema) -> NamedTemporaryFile:

    logger = get_run_logger()
    suffix = Path(file_in.name).suffix
    file_out = await get_blunk_file(suffix)

    cmd = await make_cmd(
        file_in=file_in.name,
        file_out=file_out.name,
        convert_schema=convert_schema
    )

    proc = await asyncio.create_subprocess_shell(
        cmd,
        stderr=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE
    )

    stdout, stderr = await proc.communicate()
    logger.info(f'[{cmd!r} exited with {proc.returncode}]')
    if stdout:
        logger.info(f'[stdout]\n{stdout.decode()}')
    if stderr:
        logger.error(f'[stderr]\n{stderr.decode()}')

    return file_out


@task(retries=3, retry_delay_seconds=10)
async def converted_task(
        file_in: NamedTemporaryFile,
        convert_schema: ConvertSchema) -> NamedTemporaryFile:
    logger = get_run_logger()
    try:
        file_out = await convert_file(file_in, convert_schema)
        return file_out
    except Exception as error:
        logger.error(error)

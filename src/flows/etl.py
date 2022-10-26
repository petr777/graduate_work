import asyncio
import sqlalchemy as sa
from prefect import flow
from prefect.task_runners import ConcurrentTaskRunner
from schemas import ConvertSchema
from database import session_scope
from models import MediaOriginalModel, MediaConvertModel
from aiofiles import os
from extract import extracted_task
from convert import converted_task
from upload import upload_task
from schemas import ETLSchema
from services.media_info import MediaInfoServices


async def file_video_encoding(item: dict, etl_schema: ETLSchema):
    temp_file = await extracted_task(item.get('filepath'), item.get('bucket'))
    convert_file = await converted_task(temp_file, etl_schema.convert_schema)

    upload_file = await upload_task(
        convert_file.name, etl_schema.bucket_out, etl_schema.destination_folder
    )

    info = MediaInfoServices(convert_file.name)

    movie_info = MediaConvertModel(
        bucket=etl_schema.bucket_out,
        filepath=upload_file,
        movies_id=item.get('movies_id'),
        original_id=item.get('id'),
        hash_convert=etl_schema.convert_schema.get_hash(),
        **info.short_info.dict()
    )

    async with session_scope() as session:
        session.add(movie_info)
        await session.commit()
        await session.refresh(movie_info)

    await os.remove(temp_file.name)
    await os.remove(convert_file.name)


async def get_original_not_have_convert_schema(convert_schema: ConvertSchema):
    hash_convert = convert_schema.get_hash()

    subquery = sa.select(MediaConvertModel.original_id).filter(
        MediaConvertModel.hash_convert == hash_convert)

    query = sa.select(
        MediaOriginalModel).where(MediaOriginalModel.id.notin_(subquery))

    async with session_scope() as session:
        result = await session.execute(query)
        result = result.scalars()
        data = [row.as_dict() for row in result.all()]
        return data


@flow(task_runner=ConcurrentTaskRunner(), name="start_video_encoding")
async def video_encoding(etl_schema: ETLSchema):
    convert_schema = etl_schema.convert_schema
    tasks = await get_original_not_have_convert_schema(convert_schema)
    task_video_encoding = [
        file_video_encoding(item, etl_schema=etl_schema) for item in tasks
    ]
    await asyncio.gather(*task_video_encoding)


# loop = asyncio.new_event_loop()
# loop.run_until_complete(video_encoding({'destination_folder': 'rutube', 'convert_schema': {"size": "1920x1080", "vcodec": "libx264", 'acodec': "mp3"}}))
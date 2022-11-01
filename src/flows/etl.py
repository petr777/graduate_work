import asyncio
from prefect import flow, task, get_run_logger
from prefect.task_runners import ConcurrentTaskRunner
from schemas import ConvertSchema
from database import session_scope
from models import MediaOriginalModel, MediaConvertModel
from extract import extracted_task
from convert import converted_task
from upload import upload_task
from schemas import ETLSchema
from services.media_info import MediaInfoServices
from settings import settings
from prefect.futures import PrefectFuture


async def get_state_task(task_future: PrefectFuture):
    if await task_future.wait():
        state = await task_future.get_state()
        if state.is_completed():
            return 'Success'
        return 'Error'


async def video_encoding_proccess(item, etl_schema: ETLSchema):

    temp_file_future = await extracted_task.submit(item.filepath, item.bucket)
    if await get_state_task(temp_file_future) == 'Success':
        result = await temp_file_future.result()
        convert_file_future = await converted_task.submit(
            result, etl_schema.convert_schema
        )
        if await get_state_task(convert_file_future) == 'Success':

            result = await convert_file_future.result()
            info = MediaInfoServices(result.name)

            upload_future = await upload_task.submit(
                result.name,
                etl_schema.bucket_out,
                etl_schema.destination_folder
            )

            if await get_state_task(upload_future) == 'Success':

                async with session_scope() as session:
                    convert_model = MediaConvertModel()
                    await convert_model.add_info(
                        session,
                        filepath=await upload_future.result(),
                        bucket=etl_schema.bucket_out,
                        movies_id=item.movies_id,
                        original_id=item.id,
                        hash_convert=etl_schema.convert_schema.get_hash(),
                        media_info=info.short_info
                    )
                return upload_future.result()


@flow(task_runner=ConcurrentTaskRunner(), name="video_encoding")
async def sub_flow(tasks, etl_schema: ETLSchema):
    task_video_encoding = [
        video_encoding_proccess(item, etl_schema=etl_schema) for item in tasks
    ]
    await asyncio.gather(*task_video_encoding)


@task(retries=3, retry_delay_seconds=10)
async def get_original_not_have_convert_schema(
        convert_schema: ConvertSchema,
        batch_size: int
):
    async with session_scope() as session:
        original_model = MediaOriginalModel()
        tasks = await original_model.get_original_not_have_convert_schema(
            session, convert_schema
        )
        return tasks[:batch_size]


@flow(task_runner=ConcurrentTaskRunner(), name="start_video_encoding")
async def video_encoding(etl_schema: ETLSchema):
    logger = get_run_logger()
    convert_schema = etl_schema.convert_schema
    batch_size = settings.batch_size

    future = await get_original_not_have_convert_schema.submit(
        convert_schema, batch_size
    )
    video_encoding_task = await future.result()

    if video_encoding_task:
        await sub_flow(video_encoding_task, etl_schema)

    logger.info('There are no conversion tasks for the specified parameters')

#
# loop = asyncio.new_event_loop()
# loop.run_until_complete(video_encoding(
#     {
#         'destination_folder': 'medium',
#         'convert_schema': {
#             "size": "1280x720", "vcodec": "libx264", "acodec": "aac"}
#     }
# ))

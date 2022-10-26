class MediaServiceVK:

    def __init__(self, vk_client):
        self.vk_client = vk_client

    async def get_files_in_bucket(self, bucket: str):
        paginator = self.vk_client.get_paginator('list_objects')
        async for result in paginator.paginate(Bucket=bucket):
            for content in result.get('Contents', []):
                if content.get('Size') > 0:
                    yield content.get('Key')

    async def get_file(self, bucket: str, key: str):
        response = await self.vk_client.get_object(Bucket=bucket, Key=key)
        async with response['Body'] as body:
            content = await body.read()
            return content

    async def put_file(self, bucket: str, key: str, content: bytes, ):
        await self.vk_client.put_object(Bucket=bucket, Key=key, Body=content)

from openai import AsyncOpenAI


async def get_openai():
    client = AsyncOpenAI()
    yield client

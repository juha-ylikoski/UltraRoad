import os
from openai import OpenAI


async def get_openai():
    client = OpenAI()
    yield client

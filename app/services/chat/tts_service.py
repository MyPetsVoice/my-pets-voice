import base64
import logging
import asyncio
from openai import AsyncOpenAI
from config import Config

logger = logging.getLogger(__name__)


class OpenAITTS:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=Config.OPENAI_API_KEY)
        self.voices = ['alloy', 'ash', 'ballad', 'coral', 'echo', 
                       'fable', 'nova', 'onyx', 'sage', 'shimmer']

    async def generate_speech_stream(self, voice, text):
        async with self.client.audio.speech.with_streaming_response.create(
            model="gpt-4o-mini-tts",
            voice=voice,
            input=text,
            response_format='mp3',
            instructions="Speak in a cheerful and positive tone."
        ) as response:
            async for chunk in response.iter_bytes():
                yield chunk


_tts_service = OpenAITTS()
    



# if __name__=='__main__':
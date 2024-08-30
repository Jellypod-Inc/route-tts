from enum import Enum
from typing import Literal
from pydantic import BaseModel
from elevenlabs import Voice

class Platform(Enum):
    OPENAI = "OpenAI"
    ELEVENLABS = "ElevenLabs"

class Voice(BaseModel):
    id: str
    platform: Platform

class OpenAIVoice(Voice):
    model: str
    voice: str
    platform: Platform = Platform.OPENAI
    output_format: Literal["mp3", "opus", "aac", "flac", "wav", "pcm"] = "mp3"

class ElevenLabsVoice(Voice):
    model: str
    voice: str | Voice
    platform: Platform = Platform.ELEVENLABS

class SpeechBlock(BaseModel):
    voice_id: str
    text: str
    buffer: int = 0  # Buffer in milliseconds between this speech block and the next one
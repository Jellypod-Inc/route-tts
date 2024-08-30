from enum import Enum
from typing import Literal
from pydantic import BaseModel

class Platform(Enum):
    OPENAI = "OpenAI"
    ELEVENLABS = "ElevenLabs"

class Voice(BaseModel):
    voice_id: str
    platform: Platform

class OpenAIVoice(Voice):
    model: str
    voice: str
    platform: Platform = Platform.OPENAI
    output_format: Literal["mp3", "opus", "aac", "flac", "wav", "pcm"] = "mp3"

class ElevenLabsVoice(Voice):
    platform: Platform = Platform.ELEVENLABS

class SpeechBlock(BaseModel):
    voice_id: str
    text: str
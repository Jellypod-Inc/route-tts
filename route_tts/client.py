import io
import os
from typing import List, Dict
import openai
from elevenlabs.client import ElevenLabs
from route_tts.types import OpenAIVoice, Platform, SpeechBlock, Voice
from pydub import AudioSegment

class TTS:
    def __init__(self, voices: List[Voice], openai_api_key: str = None, elevenlabs_api_key: str = None):
        self.voices: Dict[str, Voice] = {voice.voice_id: voice for voice in voices}

        self.openai_client = None
        self.elevenlabs_client = None
        
        if openai_api_key or os.getenv("OPENAI_API_KEY"):
            self.openai_client = openai.OpenAI(api_key=openai_api_key or os.getenv("OPENAI_API_KEY"))
        
        if elevenlabs_api_key or os.getenv("ELEVEN_API_KEY"):
            self.elevenlabs_client = ElevenLabs(api_key=elevenlabs_api_key or os.getenv("ELEVEN_API_KEY"))
        
    def initialize_voices(self, voices: List[Voice]):
        """
        Initialize or update the voices dictionary.
        
        This method allows adding or updating voices after the TTS instance has been created.
        It can be used if voices were not provided during initialization.
        
        :param voices: List of Voice objects to be added or updated
        """
        for voice in voices:
            self.voices[voice.voice_id] = voice

    def add_voice(self, voice: Voice):
        """
        Add a new voice to the TTS instance.

        This method allows adding a single voice after the TTS instance has been created.
        It can be used to dynamically add new voices as needed.

        :param voice: Voice object to be added
        """
        self.voices[voice.voice_id] = voice

    def remove_voice(self, voice_id: str):
        """
        Remove a voice from the TTS instance.

        This method allows removing a single voice from the TTS instance.
        It can be used to dynamically remove voices as needed.

        :param voice_id: The ID of the voice to be removed
        :raises KeyError: If the voice_id is not found in the voices dictionary
        """
        if voice_id not in self.voices:
            raise KeyError(f"Voice ID '{voice_id}' not found")
        del self.voices[voice_id]

    def list_voices(self) -> List[Voice]:
        """
        Returns a list of all available voices.

        This method provides a way to retrieve all the voices that have been
        initialized in the TTS instance.

        :return: List of Voice objects
        """
        return list(self.voices.values())
    
    # TODO: Optimze speech generation. Certain models lack context so they can be generated in parallel. 
    def generate_speech_list(self, speech_blocks: List[SpeechBlock]) -> AudioSegment:
        """
        Generate speech for multiple SpeechBlocks sequentially.

        This method takes a list of SpeechBlocks and generates audio for each one
        in sequence, returning a list of byte arrays corresponding to each input block.

        :param speech_blocks: List of SpeechBlock objects containing text and voice_id
        :return: List of generated audio as bytes, in the same order as input speech_blocks
        :raises ValueError: If any voice_id is not found or platform is unsupported
        """
        full_audio = AudioSegment.silent(duration=0)
        for speech_block in speech_blocks:
            try:
                audio_segment = self.generate_speech(speech_block)
                full_audio += audio_segment
            except Exception as e:
                raise ValueError(f"Error generating speech for block: {str(e)}")

        return full_audio

    def generate_speech(self, speech_block: SpeechBlock) -> AudioSegment:
        """
        Generate speech based on the provided SpeechBlock.
        
        This method determines the appropriate platform (OpenAI or ElevenLabs)
        and calls the corresponding speech generation method.
        
        :param speech_block: SpeechBlock containing text and voice_id
        :return: Generated audio as bytes
        :raises ValueError: If voice_id is not found or platform is unsupported
        """

        voice = self.voices.get(speech_block.voice_id)
        if not voice:
            raise ValueError(f"Voice ID '{speech_block.voice_id}' not found")

        if voice.platform == Platform.OPENAI:
            bytes = self._generate_openai_speech(voice, speech_block.text)
            return self._create_audio_segment(bytes)
        elif voice.platform == Platform.ELEVENLABS:
            pass
            # return await self._generate_elevenlabs_speech(voice, speech_block.text)
        else:
            raise ValueError(f"Unsupported platform: {voice.platform}")

    def _generate_openai_speech(self, voice: OpenAIVoice, text: str) -> bytes:
        if not self.openai_client:
            raise ValueError("OpenAI client is not initialized. Please provide a valid OpenAI API key.")

        response = openai.audio.speech.create(
            model=voice.model,
            voice=voice.voice,
            input=text
        )
        return response.content
    
    def _create_audio_segment(self, bytes) -> AudioSegment:
        return AudioSegment.from_file(io.BytesIO(bytes))  

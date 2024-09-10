import io
import os
from typing import List, Dict, Union
import openai
from elevenlabs.client import ElevenLabs
from pydantic import BaseModel
from route_tts.voices import OpenAIVoice, ElevenLabsVoice, Platform, Voice
from pydub import AudioSegment

class SpeechBlock(BaseModel):
    voice_id: str
    text: str
    buffer: int = 0  # Buffer in milliseconds between this speech block and the next one

class TTS:
    def __init__(self, voices: List[Voice], openai_api_key: str = None, elevenlabs_api_key: str = None):
        self.voices: Dict[str, Voice] = {voice.id: voice for voice in voices}

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
            self.voices[voice.id] = voice

    def add_voice(self, voice: Voice):
        """
        Add a new voice to the TTS instance.

        This method allows adding a single voice after the TTS instance has been created.
        It can be used to dynamically add new voices as needed.

        :param voice: Voice object to be added
        """
        self.voices[voice.id] = voice

    def remove_voice(self, id: str):
        """
        Remove a voice from the TTS instance.

        This method allows removing a single voice from the TTS instance.
        It can be used to dynamically remove voices as needed.

        :param id: The ID of the voice to be removed
        :raises KeyError: If the id is not found in the voices dictionary
        """
        if id not in self.voices:
            raise KeyError(f"Voice with ID '{id}' not found")
        del self.voices[id]

    def list_voices(self) -> List[Voice]:
        """
        Returns a list of all available voices.

        This method provides a way to retrieve all the voices that have been
        initialized in the TTS instance.

        :return: List of Voice objects
        """
        return list(self.voices.values())

    # TODO: Optimze speech generation. Certain models lack context so they can be generated in parallel.
    def generate_speech_list(self, speech_blocks: List[SpeechBlock], buffer: int = 0, single_output: bool = True, normalize_outputs: bool = True) -> Union[AudioSegment, List[AudioSegment]]:
        """
        Generate speech for a list of SpeechBlocks.

        This method takes a list of SpeechBlocks and generates audio for each one
        in sequence. It can return either a single combined AudioSegment or a list
        of individual AudioSegments.

        :param speech_blocks: List of SpeechBlock objects containing text and voice_id
        :param buffer: Additional buffer (in ms) to add between speech blocks
        :param single_output: If True, returns a single combined AudioSegment;
                              if False, returns a list of individual AudioSegments
        :return: Either a single AudioSegment or a list of AudioSegments
        :raises ValueError: If any voice_id is not found or if there's an error in speech generation
        """

        segments = []

        for i, speech_block in enumerate(speech_blocks):
            try:
                audio_segment = self.generate_speech(speech_block)
                if speech_block.buffer > 0:
                    audio_segment += AudioSegment.silent(duration=speech_block.buffer)
                if buffer > 0 and i < len(speech_blocks) - 1:
                    audio_segment += AudioSegment.silent(duration=buffer)

                segments.append(audio_segment)
            except Exception as e:
                raise ValueError(f"Error generating speech for block: {str(e)}")

        # Normalize the audio segments
        normalized_segments = self.normalize_audio(segments, normalize_outputs)

        if single_output:
            return sum(normalized_segments, AudioSegment.silent(duration=0))
        else:
            return normalized_segments

    def normalize_audio(self, audio_segments: List[AudioSegment], normalize_outputs: bool, target_dBFS: float = -30.0, tolerance: float = 3.0) -> List[AudioSegment]:
        """
        Softly normalize the volume of multiple AudioSegments to be closer to a target dBFS level.

        :param audio_segments: List of AudioSegments to normalize
        :param target_dBFS: Target dBFS level for normalization (default: -20.0)
        :param tolerance: Allowed deviation from target dBFS (default: 3.0)
        :return: List of normalized AudioSegments
        """
        if (not normalize_outputs):
            return audio_segments

        # Find the maximum and minimum dBFS across all segments
        max_dBFS = max(segment.dBFS for segment in audio_segments)
        min_dBFS = min(segment.dBFS for segment in audio_segments)

        # Calculate the current range and the target range
        current_range = max_dBFS - min_dBFS
        target_range = 2 * tolerance

        normalized_segments = []
        for segment in audio_segments:
            if current_range > target_range:
                # Compress the range if it's larger than the target range
                normalized_dBFS = (segment.dBFS - min_dBFS) / current_range * target_range + (target_dBFS - tolerance)
                adjustment = normalized_dBFS - segment.dBFS
                normalized_segments.append(segment.apply_gain(adjustment))
            else:
                # If the range is already small enough, just center it around the target
                center_adjustment = target_dBFS - (max_dBFS + min_dBFS) / 2
                normalized_segments.append(segment.apply_gain(center_adjustment))

        return normalized_segments

    def generate_speech(self, speech_block: SpeechBlock) -> AudioSegment:
        """
        Generate speech based on the provided SpeechBlock.

        This method determines the appropriate platform (OpenAI or ElevenLabs)
        and calls the corresponding speech generation method.

        :param speech_block: SpeechBlock containing text and id
        :return: Generated audio as bytes
        :raises ValueError: If id is not found or platform is unsupported
        """

        voice = self.voices.get(speech_block.voice_id)
        if not voice:
            raise ValueError(f"Voice ID '{speech_block.voice_id}' not found")

        if voice.platform == Platform.OPENAI:
            return self._generate_openai_speech(voice, speech_block.text)
        elif voice.platform == Platform.ELEVENLABS:
            return self._generate_elevenlabs_speech(voice, speech_block.text)
        else:
            raise ValueError(f"Unsupported platform: {voice.platform}")

    def _generate_openai_speech(self, voice: OpenAIVoice, text: str) -> AudioSegment:
        if not self.openai_client:
            raise ValueError("OpenAI client is not initialized. Please provide a valid OpenAI API key.")

        response = openai.audio.speech.create(
            model=voice.voice_model,
            voice=voice.voice,
            input=text
        )
        return self._create_audio_segment(response.content)

    def _generate_elevenlabs_speech(self, voice: ElevenLabsVoice, text: str) -> AudioSegment:
        if not self.elevenlabs_client:
            raise ValueError("ElevenLabs client is not initialized. Please provide a valid ElevenLabs API key.")

        response = self.elevenlabs_client.generate(
            model=voice.voice_model,
            voice=voice.voice,
            text=text
        )
        # Convert the generator to bytes
        audio_data = b''.join(chunk for chunk in response)
        return self._create_audio_segment(audio_data)

    def _create_audio_segment(self, audio_data: bytes) -> AudioSegment:
        return AudioSegment.from_file(io.BytesIO(audio_data))

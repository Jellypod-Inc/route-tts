import pytest
from route_tts.client import TTS
from route_tts.types import OpenAIVoice, SpeechBlock, Platform
import os

@pytest.mark.asyncio
async def test_generate_openai_speech():
    # Ensure OpenAI API key is set in environment variables
    assert os.getenv("OPENAI_API_KEY"), "OPENAI_API_KEY must be set in environment variables"

    # Initialize TTS client with an OpenAI voice
    voice = OpenAIVoice(
        voice_id="test_voice",
        model="tts-1",
        voice="alloy"
    )
    tts_client = TTS(voices=[voice])

    # Create a SpeechBlock
    speech_block = SpeechBlock(
        voice_id="test_voice",
        text="Hello, this is a test of the OpenAI text-to-speech functionality."
    )

    # Generate speech
    audio_segment = tts_client.generate_speech(speech_block)

    # Assert that we received some audio data
    assert len(audio_segment) > 0, "No audio data was generated"

    # Create output directory if it doesn't exist
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)

    # Save the audio to the output directory
    output_file = os.path.join(output_dir, "test_output.mp3")
    audio_segment.export(output_file, format="mp3")

    print("Audio saved to test_output.mp3 for manual verification")

@pytest.mark.asyncio
async def test_generate_multiple_openai_speech():
    # Ensure OpenAI API key is set in environment variables
    assert os.getenv("OPENAI_API_KEY"), "OPENAI_API_KEY must be set in environment variables"

    # Initialize TTS client with an OpenAI voice
    voice_a = OpenAIVoice(
        voice_id="test_voice_a",
        model="tts-1",
        voice="alloy"
    )
    voice_b = OpenAIVoice(
        voice_id="test_voice_b",
        model="tts-1",
        voice="nova"
    )
    tts_client = TTS(voices=[voice_a, voice_b])

    # Create SpeechBlocks
    speech_block_a = SpeechBlock(
        voice_id="test_voice_a",
        text="Hello, this is a test of the OpenAI text-to-speech functionality."
    )

    speech_block_b = SpeechBlock(
        voice_id="test_voice_b",
        text="And this is the rest of the speaking."
    )

    # Generate speech
    audio_segment = tts_client.generate_speech_list([speech_block_a, speech_block_b])

    # Assert that we received some audio data
    assert len(audio_segment) > 0, "No audio data was generated"

    # Create output directory if it doesn't exist
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)

    # Save the audio to the output directory
    output_file = os.path.join(output_dir, "test_output_multiple.mp3")
    audio_segment.export(output_file, format="mp3")

    print("Audio saved to test_output.mp3 for manual verification")
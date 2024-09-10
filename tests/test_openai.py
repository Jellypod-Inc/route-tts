import pytest
from route_tts import TTS, SpeechBlock
from route_tts.voices import OpenAIVoice
import os

OUTPUT_DIR = "output/openai"

# Initialize TTS client with OpenAI voices
voice_a = OpenAIVoice(
    id="test_voice_a",
    voice_model="tts-1",
    voice="alloy"
)
voice_b = OpenAIVoice(
    id="test_voice_b",
    voice_model="tts-1",
    voice="nova"
)
tts_client = TTS(voices=[voice_a, voice_b])

@pytest.mark.asyncio
async def test_generate_openai_speech():
    # Ensure OpenAI API key is set in environment variables
    assert os.getenv("OPENAI_API_KEY"), "OPENAI_API_KEY must be set in environment variables"

    # Create a SpeechBlock
    speech_block = SpeechBlock(
        voice_id="test_voice_a",
        text="Hello, this is a test of the OpenAI text-to-speech functionality."
    )

    # Generate speech
    audio_segment = tts_client.generate_speech(speech_block)

    # Assert that we received some audio data
    assert len(audio_segment) > 0, "No audio data was generated"

    # Create output directory if it doesn't exist
    save_audio_segment("test_output_single.mp3", audio_segment)

@pytest.mark.asyncio
async def test_generate_multiple_openai_speech():
    # Ensure OpenAI API key is set in environment variables
    assert os.getenv("OPENAI_API_KEY"), "OPENAI_API_KEY must be set in environment variables"

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

    save_audio_segment("test_output_multiple.mp3", audio_segment)


def save_audio_segment(name: str, audio_segment):
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Save the audio to the output directory
    output_file = os.path.join(OUTPUT_DIR, name)
    audio_segment.export(output_file, format="mp3")

    print(f"Audio saved to {name} for manual verification")
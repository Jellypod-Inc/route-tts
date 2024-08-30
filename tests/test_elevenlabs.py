import pytest
from route_tts import TTS, SpeechBlock
from route_tts.voices import ElevenLabsVoice
import os

OUTPUT_DIR = "output/elevenlabs"

voice_a = ElevenLabsVoice(
    id="test_elevenlabs_voice_a",
    model="eleven_monolingual_v1",
    voice="XB0fDUnXU5powFXDhCwa"
)

voice_b = ElevenLabsVoice(
    id="test_elevenlabs_voice_b",
    model="eleven_monolingual_v1",
    voice="OYTbf65OHHFELVut7v2H"
)

tts_client = TTS(voices=[voice_a, voice_b])

@pytest.mark.asyncio
async def test_generate_elevenlabs_speech():
    # Ensure ElevenLabs API key is set in environment variables
    assert os.getenv("ELEVEN_API_KEY"), "ELEVEN_API_KEY must be set in environment variables"

    # Create a SpeechBlock
    speech_block = SpeechBlock(
        voice_id="test_elevenlabs_voice_a",
        text="Hello, this is a test of the ElevenLabs text-to-speech functionality."
    )

    # Generate speech
    audio_segment = tts_client.generate_speech(speech_block)

    # Assert that we received some audio data
    assert len(audio_segment) > 0, "No audio data was generated"

    save_audio_segment("test_output_single.mp3", audio_segment)

@pytest.mark.asyncio
async def test_generate_multiple_elevenlabs_speech():
    # Ensure ElevenLabs API key is set in environment variables
    assert os.getenv("ELEVEN_API_KEY"), "ELEVEN_API_KEY must be set in environment variables"

    # Initialize TTS client with ElevenLabs voices

    # Create SpeechBlocks
    speech_block_a = SpeechBlock(
        voice_id="test_elevenlabs_voice_a",
        text="Hello, this is a test of the ElevenLabs text-to-speech functionality."
    )

    speech_block_b = SpeechBlock(
        voice_id="test_elevenlabs_voice_b",
        text="And this is the rest of the speaking using a different voice."
    )

    # Generate speech
    audio_segment = tts_client.generate_speech_list([speech_block_a, speech_block_b])
    assert len(audio_segment) > 0, "No audio data was generated"
    save_audio_segment("test_output_multiple.mp3", audio_segment)

    # Generate speech with buffer
    audio_segment_buffer = tts_client.generate_speech_list([speech_block_a, speech_block_b], buffer=5000)
    assert len(audio_segment) > 0, "No audio data was generated"
    save_audio_segment("test_output_multiple_with_buffer.mp3", audio_segment_buffer)

@pytest.mark.asyncio
async def test_generate_multiple_elevenlabs_speech_different_buffers():
    # Ensure ElevenLabs API key is set in environment variables
    assert os.getenv("ELEVEN_API_KEY"), "ELEVEN_API_KEY must be set in environment variables"

    # Initialize TTS client with ElevenLabs voices

    # Create SpeechBlocks
    speech_block_a = SpeechBlock(
        voice_id="test_elevenlabs_voice_a",
        text="What's up! This is a test of the ElevenLabs text-to-speech functionality.",
        buffer=2000
    )

    speech_block_b = SpeechBlock(
        voice_id="test_elevenlabs_voice_b",
        text="And this is the rest of the speaking using a different voice.",
        buffer=5000
    )

    speech_block_c = SpeechBlock(
        voice_id="test_elevenlabs_voice_a",
        text="Here I am again! Hi."
    )

    # Generate speech
    audio_segment = tts_client.generate_speech_list([speech_block_a, speech_block_b, speech_block_c])
    assert len(audio_segment) > 0, "No audio data was generated"
    save_audio_segment("test_output_multiple_with_different_buffers.mp3", audio_segment)

def save_audio_segment(name: str, audio_segment): 
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Save the audio to the output directory
    output_file = os.path.join(OUTPUT_DIR, name)
    audio_segment.export(output_file, format="mp3")

    print(f"Audio saved to {name} for manual verification")
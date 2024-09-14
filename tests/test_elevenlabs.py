import pytest
from route_tts import TTS, SpeechBlock
from route_tts.voices import ElevenLabsVoice
import os

OUTPUT_DIR = "output/elevenlabs"

voice_a = ElevenLabsVoice(
    id="test_elevenlabs_voice_a",
    voice_model="eleven_turbo_v2_5",
    voice="pBZVCk298iJlHAcHQwLr"
)

voice_b = ElevenLabsVoice(
    id="test_elevenlabs_voice_b",
    voice_model="eleven_turbo_v2_5",
    voice="iP95p4xoKVk53GoZ742B"
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

@pytest.mark.asyncio
async def test_generate_multiple_elevenlabs_speech():
    # Ensure ElevenLabs API key is set in environment variables
    assert os.getenv("ELEVEN_API_KEY"), "ELEVEN_API_KEY must be set in environment variables"

    # Initialize TTS client with ElevenLabs voices

    # Create SpeechBlocks
    speech_block_a = SpeechBlock(
        voice_id="test_elevenlabs_voice_a",
        text="I'm normally a bit quieter of a voice, but after normalizing, it should be better!"
    )

    speech_block_b = SpeechBlock(
        voice_id="test_elevenlabs_voice_b",
        text="Yes this is great. I can hear you much better now"
    )

    speech_block_c = SpeechBlock(
        voice_id="test_elevenlabs_voice_a",
        text="Perfect - we're all good to go!"
    )

    # Generate speech
    audio_segment = tts_client.generate_speech_list([speech_block_a, speech_block_b, speech_block_c], normalize_outputs=True)
    assert len(audio_segment) > 0, "No audio data was generated"
    save_audio_segment("test_output_multiple_normalized.mp3", audio_segment)

@pytest.mark.asyncio
async def test_generate_multiple_elevenlabs_speech_same_voice():
    # Ensure ElevenLabs API key is set in environment variables
    assert os.getenv("ELEVEN_API_KEY"), "ELEVEN_API_KEY must be set in environment variables"

    # Create 5 SpeechBlocks with the same voice
    speech_blocks = [
        SpeechBlock(
            voice_id="test_elevenlabs_voice_a",
            text=f"This is speech block number {i + 1}. Testing multiple blocks with the same voice."
        ) for i in range(3)
    ]

    # Generate speech
    audio_segment = tts_client.generate_speech_list(speech_blocks, normalize_outputs=True)
    assert len(audio_segment) > 0, "No audio data was generated"
    save_audio_segment("test_output_multiple_same_voice.mp3", audio_segment)

@pytest.mark.asyncio
async def test_generate_multiple_elevenlabs_speech_continuous_context():
    # Ensure ElevenLabs API key is set in environment variables
    assert os.getenv("ELEVEN_API_KEY"), "ELEVEN_API_KEY must be set in environment variables"

    # Create distinct speech blocks with continuous context
    speech_blocks = [
        SpeechBlock(
            voice_id="test_elevenlabs_voice_a",
            text="Once upon a time, in a land far away, there was a magical forest."
        ),
        SpeechBlock(
            voice_id="test_elevenlabs_voice_a",
            text="In this forest lived a wise old owl who knew all the secrets of the trees."
        ),
        SpeechBlock(
            voice_id="test_elevenlabs_voice_a",
            text="One day, a young adventurer stumbled upon the forest, seeking the owl's wisdom."
        )
    ]

    # Generate speech
    audio_segment = tts_client.generate_speech_list(speech_blocks, normalize_outputs=True)
    assert len(audio_segment) > 0, "No audio data was generated"
    save_audio_segment("test_output_continuous_context.mp3", audio_segment)

@pytest.mark.asyncio
async def test_generate_multiple_elevenlabs_speech_continuous_context_no_request_stiching():
    # Ensure ElevenLabs API key is set in environment variables
    assert os.getenv("ELEVEN_API_KEY"), "ELEVEN_API_KEY must be set in environment variables"

    # Create distinct speech blocks with continuous context
    speech_blocks = [
        SpeechBlock(
            voice_id="test_elevenlabs_voice_a",
            text="Once upon a time, in a land far away, there was a magical forest."
        ),
        SpeechBlock(
            voice_id="test_elevenlabs_voice_a",
            text="In this forest lived a wise old owl who knew all the secrets of the trees."
        ),
        SpeechBlock(
            voice_id="test_elevenlabs_voice_a",
            text="One day, a young adventurer stumbled upon the forest, seeking the owl's wisdom."
        )
    ]

    # Generate speech
    audio_segment = tts_client.generate_speech_list(speech_blocks, normalize_outputs=True, request_stitching=False)
    assert len(audio_segment) > 0, "No audio data was generated"
    save_audio_segment("test_output_continuous_context_no_stitching.mp3", audio_segment)

def save_audio_segment(name: str, audio_segment):
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Save the audio to the output directory
    output_file = os.path.join(OUTPUT_DIR, name)
    audio_segment.export(output_file, format="mp3")

    print(f"Audio saved to {name} for manual verification")
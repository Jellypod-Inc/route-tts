import os
import requests
from typing import Dict, Any, Optional

class CustomElevenLabsClient:
    BASE_URL = "https://api.elevenlabs.io/v1"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        if not self.api_key:
            raise ValueError("No API key provided. Please provide an API key or set the ELEVEN_API_KEY environment variable.")
        self.headers = {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json"
        }

    # Ref: https://elevenlabs.io/docs/api-reference/how-to-use-request-stitching
    def generate_speech_with_conditioning(
        self,
        text: str,
        voice_id: str,
        model_id: str,
        voice_settings: Optional[Dict[str, Any]] = None,
        previous_request_ids: Optional[list] = None,
        previous_text: Optional[str] = None,
        next_text: Optional[str] = None
    ) -> requests.Response:
        url = f"{self.BASE_URL}/text-to-speech/{voice_id}"

        payload = {
            "text": text,
            "model_id": model_id,
            "voice_settings": voice_settings,
        }

        if previous_request_ids:
            payload["previous_request_ids"] = previous_request_ids[-3:]
        if previous_text is not None:
            payload["previous_text"] = previous_text
        if next_text is not None:
            payload["next_text"] = next_text

        response = requests.post(url, json=payload, headers=self.headers)

        if response.status_code == 200:
            return response
        else:
            raise Exception(f"Error generating speech: {response.text}")

# Example usage:
# def main():
#     client = ElevenLabsClient("your-api-key-here")
#     voice_id = "21m00Tcm4TlvDq8ikWAM"  # Rachel
#     paragraphs = [
#         "The advent of technology has transformed countless sectors, with education "
#         "standing out as one of the most significantly impacted fields.",
#         "In recent years, educational technology, or EdTech, has revolutionized the way "
#         "teachers deliver instruction and students absorb information.",
#         # ... more paragraphs ...
#     ]
#
#     previous_request_ids = []
#     audio_segments = []
#
#     for i, paragraph in enumerate(paragraphs):
#         is_first_paragraph = i == 0
#         is_last_paragraph = i == len(paragraphs) - 1
#
#         audio_data, request_id = client.generate_speech_with_conditioning(
#             text=paragraph,
#             voice_id=voice_id,
#             previous_request_ids=previous_request_ids,
#             previous_text=None if is_first_paragraph else " ".join(paragraphs[:i]),
#             next_text=None if is_last_paragraph else " ".join(paragraphs[i + 1:])
#         )
#
#         previous_request_ids.append(request_id)
#         audio_segments.append(audio_data)
#         print(f"Successfully converted paragraph {i + 1}/{len(paragraphs)}")
#
#     # Here you would combine the audio segments and save the result

# if __name__ == "__main__":
#     main()

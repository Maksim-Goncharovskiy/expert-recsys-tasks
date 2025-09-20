import requests
from .model import ASRApi
from .exceptions import ApiError




class FireworksApi(ASRApi):
    url = "https://audio-turbo.us-virginia-1.direct.fireworks.ai/v1/audio/transcriptions"

    data = {
            "model": "whisper-v3-turbo",
            "temperature": "0",
            "vad_model": "silero"
        }
    
    def __init__(self, api_key: str):
        super().__init__(api_key)
    

    def transcribe(self, audio_file: bytes) -> str:
        response = requests.post(
            url=self.url,
            headers={"Authorization": f"Bearer {self.api_key}"},
            files={"file": audio_file},
            data=self.data
        )

        if response.status_code == 200:
            return response.json()['text']
        else:
            raise ApiError(f"Something went wrong.\nStatus code: {response.status_code}\nError text: {response.text}")
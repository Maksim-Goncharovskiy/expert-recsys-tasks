import requests
from .model import ASRApi
from .exceptions import ApiError



class NexaraApi(ASRApi):
    url = "https://api.nexara.ru/api/v1/audio/transcriptions"

    data = {
        "response_format": "json",
    }
    
    def __init__(self, api_key: str):
        super().__init__(api_key)
    

    def transcribe(self, audio_file: bytes) -> str:
        response = requests.post(
            url=self.url,
            headers={"Authorization": f"Bearer {self.api_key}"},
            files={"file": ("", audio_file, "audio/wav")},
            data=self.data
        )

        if response.status_code == 200:
            return response.json()['text']
        else:
            raise ApiError(f"Something went wrong.\nStatus code: {response.status_code}\nError text: {response.text}")
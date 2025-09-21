import requests
from requests import Response
from .model import ASRApi
from .exceptions import ApiError


class FireworksApi(ASRApi):
    def __init__(self, name: str, url: str, api_key: str):
        super().__init__(name, url, api_key)

    def transcribe(self, audio_file: bytes) -> str:
        response: Response = requests.post(
            url=self._url,
            headers={"Authorization": f"Bearer {self._api_key}"},
            files={"file": audio_file},
            data={
                "model": "whisper-v3-turbo",
                "temperature": "0",
                "vad_model": "silero",
            },
        )

        if response.status_code == 200:
            return response.json()["text"]
        else:
            raise ApiError(
                f"Something went wrong.\nStatus code: {response.status_code}\nError text: {response.text}"
            )

from abc import ABCMeta, abstractmethod



class ASRApi(metaclass=ABCMeta):
    def __init__(self, api_key: str):
        self.api_key = api_key 


    @abstractmethod
    def transcribe(self, audio_file: bytes) -> str:
        pass
from abc import ABCMeta, abstractmethod


class ASRApi(metaclass=ABCMeta):
    def __init__(self, name: str, url: str, api_key: str):
        self.name: str = name

        self._url: str = url
        self._api_key: str = api_key

    @abstractmethod
    def transcribe(self, audio_file: bytes) -> str:
        """
        Обращение к API для получения транскрипции аудиофайла.
        Параметры:
            * audio_file: bytes - последовательность байтов прочитанного аудиофайла.
        """
        pass

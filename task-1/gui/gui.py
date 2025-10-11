import streamlit as st
from streamlit.runtime.uploaded_file_manager import UploadedFile
import jiwer

from api import ASRApi, ApiError

import time


def run_gui_app(api1: ASRApi, api2: ASRApi):
    """
    Конструирует streamlit-приложение.
    Параметры:
        * api1, api2: ASRApi - сравниваемые Api сервисы
    """
    st.set_page_config(page_title="Сравнение сервисов транскрибации")

    st.markdown(
        "<h1 style='text-align: center; color: black;'>Сравнение сервисов транскрибации</h1>",
        unsafe_allow_html=True,
    )

    st.markdown(
        "<h4 style='color: black;'>1. Загрузите аудиофайл.</h4>", unsafe_allow_html=True
    )
    audio_file: UploadedFile = st.file_uploader("Audio", type=["wav"])

    st.markdown(
        "<h4 style='color: black;'>2. (Опционально)Загрузите файл с транскрипцией для расчёта метрики WER.</h4>",
        unsafe_allow_html=True,
    )
    text_file: UploadedFile = st.file_uploader("Text", type=["txt"])

    _, col2, _ = st.columns([1, 1, 1])
    st.markdown(
        """
        <style>
        div.stButton > button:first-child {
            background-color: #00cc00; 
            color: white;
            font-size: 20px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    start_button = col2.button("Получить транскрипции", disabled=not audio_file)

    if start_button and audio_file:
        st.markdown(
            "<h3 style='text-align: center; color: black;'>Результат</h3>",
            unsafe_allow_html=True,
        )
        col1, col2 = st.columns(2)
        col1.markdown(
            f"<h4 style='text-align: center; color: black;'>{api1.name}</h4>",
            unsafe_allow_html=True,
        )
        col2.markdown(
            f"<h4 style='text-align: center; color: black;'>{api2.name}</h4>",
            unsafe_allow_html=True,
        )

        api1_start_time: float = time.time()
        try:
            api1_transcription: str = api1.transcribe(audio_file=audio_file.getvalue())
        except ApiError as err:
            api1_transcription: str = "Ошибка в процессе обращения к API"
            print(err)
        api1_time: float = time.time() - api1_start_time

        api2_start_time: float = time.time()

        try:
            api2_transcription: str = api2.transcribe(audio_file=audio_file.getvalue())
        except ApiError as err:
            api2_transcription: str = "Ошибка в процессе обращения к API"
            print(err)

        api2_time: float = time.time() - api2_start_time

        col1.text_area("Transcription", api1_transcription, height=200)
        col2.text_area("Transcription", api2_transcription, height=200)

        if text_file:
            reference: str = text_file.read().decode("utf-8")
            api1_wer: float = jiwer.wer(reference, api1_transcription)
            api2_wer: float = jiwer.wer(reference, api2_transcription)

            col1.text(f"WER: {api1_wer:.2f}")
            col2.text(f"WER: {api2_wer:.2f}")

        col1.text(f"Время, cек: {api1_time:.2f}")
        col2.text(f"Время, cек: {api2_time:.2f}")

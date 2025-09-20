import streamlit as st

from config import Config, load_config
from api import ASRApi, FireworksApi, NexaraApi, ApiError

import time


def main():
    config: Config = load_config()
    fw_api = FireworksApi(api_key=config.fw_api_key)
    nexara_api = NexaraApi(api_key=config.nexara_api_key)

    st.set_page_config(
        page_title="Сравнение сервисов транскрибации"
    )

    uploaded_file = st.file_uploader("Загрузите аудио файл", type=["wav"])
    start_button = st.button("Начать", disabled=not uploaded_file)

    if start_button and uploaded_file:

        col1, col2 = st.columns(2)
        col1.subheader("Сервис1")
        col2.subheader("Сервис2")
        col1.text_area("Результат-1", "Текст 1 1 1", height=200)
        col2.text_area("Результат-2", "Текст 2 2 2", height=200)




if __name__ == "__main__":
    main()
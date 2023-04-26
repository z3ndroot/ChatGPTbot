import asyncio
import logging
import os

import torch
from langdetect import detect
from transliterate import translit


class Announcer:

    def __init__(self, config: dict):
        self.device = torch.device(config['device'])
        torch.set_num_threads(4)
        self.url_model = {f"models/{config['ru_model_speech']}": 'https://models.silero.ai/models/tts/ru/v3_1_ru.pt',
                          f"models/{config['en_model_speech']}": 'https://models.silero.ai/models/tts/en/v3_en.pt'}
        self.__check_model(f"models/{config['ru_model_speech']}")
        self.__check_model(f"models/{config['en_model_speech']}")
        self._config = config

    async def voicing(self, message: str, chat_id: str):
        path_audio = []
        if detect(message) not in ('ru', 'en'):
            logging.warning('Message language not recognized')
            return
        chunks = [message[i:i + 900] for i in range(0, len(message), 900)]

        for n, chunk in enumerate(chunks):

            if detect(message) == "ru":
                path_voice = await self.__speak_text(
                    message=self.__translit(chunk),
                    local_file=self.__check_model(f"models/{self._config['ru_model_speech']}"),
                    speaker=self._config['ru_speaker'],
                    filename=f'{chat_id}_{n}'
                )

                path_audio.append(path_voice)

            if detect(message) == "en":
                path_voice = await self.__speak_text(
                    message=chunk,
                    local_file=self.__check_model(f"models/{self._config['en_model_speech']}"),
                    speaker=self._config['en_speaker'],
                    filename=f'{chat_id}_{n}'
                )
                path_audio.append(path_voice)

        return path_audio

    async def __speak_text(self, message: str, local_file: str, speaker: str, filename: str):
        model = torch.package.PackageImporter(local_file).load_pickle('tts_models', 'model')
        model.to(self.device)
        audio_paths = await asyncio.to_thread(
            model.save_wav,
            text=message,
            speaker=speaker,
            sample_rate=self._config["sample_rate"],
            audio_path=f'voice/{filename}.wav'
        )
        logging.info("_Successful text-to-audio verification_")
        return audio_paths

    def __check_model(self, model_speech: str):
        if not os.path.isfile(model_speech):
            logging.info(f'Model {model_speech} is missing and will be installed')
            torch.hub.download_url_to_file(self.url_model[model_speech], model_speech)

        return model_speech

    def __translit(self, text: str):
        return translit(text, 'ru')

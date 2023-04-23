import logging
import os

import torch
from langdetect import detect
from transliterate import translit


class Announcer:

    def __init__(self, config: dict):
        self.device = torch.device(config['device'])
        torch.set_num_threads(4)
        self.url_model = {config['ru_model_speech']: 'https://models.silero.ai/models/tts/ru/v3_1_ru.pt',
                          config['en_model_speech']: 'https://models.silero.ai/models/tts/en/v3_en.pt'}
        self.__check_model(config['ru_model_speech'])
        self.__check_model(config['en_model_speech'])
        self._config = config

    def voicing(self, message: str, chat_id: str):
        if detect(message) not in ('ru', 'en'):
            logging.warning('Message language not recognized')
            return

        if detect(message) == "ru":
            path_voice = self.__speak_text(
                message=self.__translit(message),
                local_file=self.__check_model(self._config['ru_model_speech']),
                speaker=self._config['ru_speaker'],
                filename=chat_id
            )

            return path_voice

        if detect(message) == "en":
            path_voice = self.__speak_text(
                message=message,
                local_file=self.__check_model(self._config['en_model_speech']),
                speaker=self._config['en_speaker'],
                filename=chat_id
            )
            return path_voice

    def __speak_text(self, message: str, local_file: str, speaker: str, filename: str):
        model = torch.package.PackageImporter(local_file).load_pickle('tts_models', 'model')
        model.to(self.device)
        audio_paths = model.save_wav(text=message,
                                     speaker=speaker,
                                     sample_rate=self._config["sample_rate"],
                                     audio_path=f'voice/{filename}.wav')
        logging.info("_Successful text-to-audio verification_")
        return audio_paths

    def __check_model(self, model_speech: str):
        if not os.path.isfile(model_speech):
            logging.info(f'Model {model_speech} is missing and will be installed')
            torch.hub.download_url_to_file(self.url_model[model_speech], model_speech)

        return model_speech

    def __translit(self, text: str):
        return translit(text, 'ru')

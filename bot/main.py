import logging
import os

from dotenv import load_dotenv
from telegram_bot import TelegramBot
from chatai import GPT
from voicing import Announcer
from openai import api_base


def check_folders(folders: list):
    """
    Creating folders if they are missing
    :param folders:
    :return: list missing folders
    """
    missing_folder = []
    for folder in folders:
        if not os.path.isdir(folder):
            os.mkdir(folder)
            missing_folder.append(folder)
    return missing_folder


def main():
    # Read .env file
    load_dotenv()

    # Check missing folders
    folders = ['audio', 'history', 'log', 'models', 'voice']
    missing_folder = check_folders(folders)

    # Setup logging
    file_log = logging.FileHandler('log/chat.log')
    console_out = logging.StreamHandler()
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO,
                        handlers=(file_log, console_out))

    if len(missing_folder) > 0:
        logging.info(f'These folders {", ".join(missing_folder)} were missing and were successfully created')

    # Check if the required environment variables are set
    required_values = ['TOKEN_TELEGRAM', 'TOKEN_OPENAI']
    missing_values = [value for value in required_values if os.environ.get(value) is None]
    if len(missing_values) > 0:
        logging.error(f'The following environment values are missing in your .env: {", ".join(missing_values)}')
        exit(1)

    # Setup configurations
    openai_config = {"token_openai": os.environ['TOKEN_OPENAI'],
                     'proxy': os.environ.get('PROXY', None),
                     'model': os.environ.get('MODEL', 'gpt-3.5-turbo-0301'),
                     'base_api': os.environ.get('BASE_API', api_base),
                     'image_size': os.environ.get('IMAGE_SIZE', '512x512'),
                     'max_tokens': int(os.environ.get('MAX_TOKENS', 1200)),
                     'max_all_tokens': int(os.environ.get('MAX_ALL_TOKENS', 4097)),
                     'temperature': float(os.environ.get('TEMPERATURE', 1.0)),
                     'presence_penalty': float(os.environ.get('PRESENCE_PENALTY', 0.0)),
                     'frequency_penalty': float(os.environ.get('FREQUENCY_PENALTY', 0.0)),
                     }

    telegram_config = {'token_bot': os.environ['TOKEN_TELEGRAM'],
                       'allowed_user_ids': os.environ.get('ALLOWED_TELEGRAM_USER_IDS', '*'),
                       'stream': os.environ.get('STREAM', 'true').lower() == "true"}

    voicing_config = {'ru_model_speech': os.environ.get('RU_MODEL_SPEECH', 'ru_v3.pt'),
                      'en_model_speech': os.environ.get('EN_MODEL_SPEECH', 'v3_en.pt'),
                      'ru_speaker': os.environ.get('RU_SPEAKER', 'baya'),
                      'en_speaker': os.environ.get('EN_SPEAKER', 'en_1'),
                      'sample_rate': int(os.environ.get('SAMPLE_RATE', 48000)),
                      'device': os.environ.get('DEVICE', 'cpu')
                      }

    openai_chat = GPT(config=openai_config)
    announcer = Announcer(config=voicing_config)
    telegram_bot = TelegramBot(config=telegram_config, gpt=openai_chat, announcer=announcer)
    telegram_bot.run()


if __name__ == '__main__':
    main()

# ChatGPTBot Telegram
![python-version](https://img.shields.io/badge/python-3.9.7-blue)
[![openai-version](https://img.shields.io/badge/openai-0.27.4-orange.svg)](https://openai.com/)
[![silero-version](https://img.shields.io/badge/silero-0.4.1-orange)](https://silero.ai/)
[![aiogram-version](https://img.shields.io/badge/aiogram-2.25.1-blue)](https://aiogram.dev/)

## Description

This project is a Telegram bot that utilizes OpenAI to generate images, create a chat with context preservation, and recognize voice messages. The bot is built on Python and uses OpenAI and Aiogram libraries. Additionally, it incorporates the Silero Text-to-Speech model for audio output.

## Features

- Image generation using OpenAI
- Context preservation for chat history
- Voice message recognition
- Text-to-speech audio output

## Installation

Clone the repository and navigate to the project directory:

```shell
git clone 
cd chatgpt-telegram-bot
```

#### From Source
1. Create a virtual environment:
```shell
python -m venv venv
```

2. Activate the virtual environment:
```shell
# For Linux or macOS:
source venv/bin/activate

# For Windows:
venv\Scripts\activate
```

3. Install the dependencies using `requirements.txt` file:
```shell
pip install -r requirements.txt
```

4. Use the following command to start the bot:
```
python bot/main.py
```


## Usage

1. Start the bot by sending a message to the bot username.

2. Use the available commands to interact with the bot:

- /image - Generates an image using OpenAI.
- /system_message - Sends a system message to OpenAI GPT.
- /clear - Clears the chat history.
- /help - Displays the list of available commands.


## Credits

- OpenAI
- Aiogram
- Silero Text-to-Speech Model

## License

This project is licensed under the MIT License - see the LICENSE file for details.
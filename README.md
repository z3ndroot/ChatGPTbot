# ChatGPTBot Telegram

![python-version](https://img.shields.io/badge/python-3.9.7-blue)
[![openai-version](https://img.shields.io/badge/openai-0.27.4-orange.svg)](https://openai.com/)
[![silero-version](https://img.shields.io/badge/silero-0.4.1-orange)](https://silero.ai/)
[![aiogram-version](https://img.shields.io/badge/aiogram-2.25.1-blue)](https://aiogram.dev/)

## Description

This project is a Telegram bot that utilizes OpenAI to generate images, create a chat with context preservation, and
recognize voice messages. The bot is built on Python and uses OpenAI and Aiogram libraries. Additionally, it
incorporates the Silero Text-to-Speech model for audio output.

## Features

- Image generation using OpenAI
- Context preservation for chat history
- Voice message recognition
- Text-to-speech audio output

### Configuration

Set up the configuration by copying `.env.example` and renaming it to `.env`.

| Parameter                   | Description                                                                                                                                                                                                  |
|-----------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `TOKEN_OPENAI`              | OpenAI API key, you can get it from [here](https://platform.openai.com/account/api-keys)                                                                                                                     |
| `TOKEN_TELEGRAM`            | Telegram bot's token, obtained using [BotFather](http://t.me/botfather) (see [tutorial](https://core.telegram.org/bots/tutorial#obtain-your-bot-token))                                                      |
| `ALLOWED_TELEGRAM_USER_IDS` | A comma-separated list of Telegram user IDs that are allowed to interact with the bot (use [@getmyid_bot](https://t.me/getmyid_bot) to find your user ID). **Note**: by default, *everyone* is allowed (`*`) |

#### Additional optional configuration options

| Parameter           | Description                                                                                                           | Default value               |
|---------------------|-----------------------------------------------------------------------------------------------------------------------|-----------------------------|
| `MODEL`             | The OpenAI model to use for generating responses                                                                      | `gpt-3.5-turbo`             |
| `STREAM`            | Whether to stream responses.                                                                                          | `true`                      |
| `MAX_TOKENS`        | Upper bound on how many tokens the ChatGPT API will return                                                            | `1200`                      |
| `MAX_ALL_TOKENS`    | Maximum value of history size in tokens                                                                               | `4097`                      |
| `TEMPERATURE`       | Number between 0 and 2. Higher values will make the output more random                                                | `1.0`                       |
| `PRESENCE_PENALTY`  | Number between -2.0 and 2.0. Positive values penalize new tokens based on whether they appear in the text so far      | `0.0`                       |
| `FREQUENCY_PENALTY` | Number between -2.0 and 2.0. Positive values penalize new tokens based on their existing frequency in the text so far | `0.0`                       |
| `IMAGE_SIZE`        | The DALL·E generated image size. Allowed values: `256x256`, `512x512` or `1024x1024`                                  | `512x512`                   |
| `PROXY`             | Proxy to be used for OpenAI and Telegram bot (e.g. `http://localhost:8080`)                                           | `None`                      |
| `BASE_API`          | It is used to specify the endpoint for the API request                                                                | `https://api.openai.com/v1` |

Check out the [official API reference](https://platform.openai.com/docs/api-reference/chat) for more details.

#### Additional settings for the voice model

| Parameter         | Description                                    | Default value |
|-------------------|------------------------------------------------|---------------|
| `RU_MODEL_SPEECH` | Id of the Russian model                        | `ru_v3.pt`    |
| `EN_MODEL_SPEECH` | Id of the English model                        | `v3_en.pt`    |
| `RU_SPEAKER`      | Russian announcer's voice                      | `baya`        |
| `EN_SPEAKER`      | English voice-over                             | `en_1`        |
| `SAMPLE_RATE`     | Number of sound samples transmitted per second | `48000`       |
| `DEVICE`          | Selected device                                | `cpu`         |

Check out the [Official Documentation](https://github.com/snakers4/silero-models) for more details.

## Installation

Clone the repository and navigate to the project directory:

```shell
git clone https://github.com/z3ndroot/ChatGPTbot
cd ChatGPTbot
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

- /clear - Cleaning up the conversation
- /system_role - Provides initial instructions for the model
- /image - Generates an image by prompt
- /help - I'll show you how to use this bot

## Credits

- OpenAI
- Aiogram
- Silero Text-to-Speech Model

## License

This project is licensed under the MIT License - see the LICENSE file for details.

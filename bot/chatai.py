import json
import logging

import openai
import soundfile as sf
import tiktoken
from openai.error import InvalidRequestError
import os


class GPT:
    def __init__(self, config: dict):
        openai.api_key = config["token_openai"]
        self._config = config

    async def create_chat(self, message: list, chat_id: str):
        """
        Stream response from the GTP model
        :param message: Message from user
        :param chat_id: Telegram chat id
        :return: The answer from the model or 'not_finished'
        """
        history = self.__read_file(chat_id)['history']
        history.append({"role": "user", "content": message})
        token_len = self.num_tokens_from_messages(history)
        answer = ''
        if token_len + self._config['max_tokens'] > self._config['max_all_tokens']:
            logging.warning(
                f"This model's maximum context length is 4097 tokens."
                f" {token_len} in the messages, 1200 in the completion")
            summarize = await self.__summarise(history[:-1])
            self.clear_history(chat_id)
            history = self.__read_file(chat_id)['history']
            history.append({"role": "assistant", "content": summarize})
            history.append({"role": "user", "content": message})

        response = await self._get_chat_response(history)

        async for item in response:
            if 'choices' not in item or len(item.choices) == 0:
                continue
            delta = item.choices[0].delta
            if 'content' in delta:
                answer += delta.content
                yield answer, 'not_finished'
        answer = answer.strip()
        history.append({"role": "assistant", "content": answer})
        self.__add_to_history(history, chat_id)
        yield answer

    async def generate_image(self, prompt: str):
        """
        Generates images with DALL·E on prompt
        :param prompt: The prompt to send to the model
        :return: The image URL
        """
        try:
            response = await openai.Image.acreate(
                prompt=prompt,
                n=1,
                size=self._config["image_size"]
            )
            image_url = response['data'][0]['url']
            return image_url
        except InvalidRequestError as e:
            return e.user_message

    async def transcriptions(self, chat_id: str):
        """
        Transcribes the audio file using the Whisper model.
        :param chat_id: Telegram chat id
        :return: Text decoding of audio
        """
        with open(f"audio/{chat_id}.wav", "rb") as audio:
            result = await openai.Audio.atranscribe("whisper-1", audio)

            return result.text

    async def convert_audio(self, chat_id):
        """
        Converts the .ogg file format to .wav
        """
        ogg_file = f"audio/{chat_id}.ogg"
        wav_file = f"audio/{chat_id}.wav"

        data, samplerate = sf.read(ogg_file)
        sf.write(wav_file, data, samplerate)

    async def _get_chat_response(self, message: list[dict]):
        """
        Request a response from the GPT model
        :param message: The message to send to the model
        :return: The response from the model
        """
        return await openai.ChatCompletion.acreate(
            model=self._config["model"],
            messages=message,
            temperature=self._config["temperature"],
            max_tokens=self._config["max_tokens"],
            n=self._config["n_choices"],
            presence_penalty=self._config["presence_penalty"],
            frequency_penalty=self._config["frequency_penalty"],
            stream=True)

    def num_tokens_from_messages(self, messages, model="gpt-3.5-turbo-0301"):
        """Returns the number of tokens used by a list of messages."""
        try:
            encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            encoding = tiktoken.get_encoding("cl100k_base")
        if model == self._config["model"]:  # note: future models may deviate from this
            num_tokens = 0
            for message in messages:
                num_tokens += 4  # every message follows <im_start>{role/name}\n{content}<im_end>\n
                for key, value in message.items():
                    num_tokens += len(encoding.encode(value))
                    if key == "name":  # if there's a name, the role is omitted
                        num_tokens += -1  # role is always required and always 1 token
            num_tokens += 2  # every reply is primed with <im_start>assistant
            return num_tokens

    async def __summarise(self, conversation) -> str:
        """
        Summarises the conversation history.
        :param conversation: The conversation history
        :return: The summary
        """
        messages = [
            {"role": "assistant", "content": "Summarize this conversation in 700 characters or less"},
            {"role": "user", "content": str(conversation)}
        ]
        response = await openai.ChatCompletion.acreate(
            model=self._config["model"],
            messages=messages,
            temperature=0.4
        )
        return response.choices[0]['message']['content']

    def __write_to_file(self, data, chat_id: str):
        with open(f'history/{chat_id}.json', "w", encoding="UTF8") as file:
            json.dump(data, file, indent=4)

    def __read_file(self, chat_id: str):
        with open(f'history/{chat_id}.json', "r", encoding="UTF8") as file:
            return json.load(file)

    def create_user_history(self, chat_id, username):
        if not os.path.isfile(f'history/{chat_id}.json'):
            self.__write_to_file({
                'username': username,
                'history': [{"role": "system", "content": ""}],
            }, chat_id)

    def __add_to_history(self, history: list, chat_id):
        """
        Функция сохранения истории чата
        """
        result = self.__read_file(chat_id)
        result['history'] = history
        self.__write_to_file(result, chat_id)

    def system_message(self, message: str, chat_id):
        result = self.__read_file(chat_id)
        result['history'][0].update({"content": message})
        self.__write_to_file(result, chat_id)

    def clear_history(self, chat_id: str):
        """
        Функция очистки истории чата
        """
        result = self.__read_file(chat_id)
        result['history'] = [{"role": "system", "content": ""}]
        self.__write_to_file(result, chat_id)
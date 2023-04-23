import asyncio
import logging

from aiogram import Bot
from aiogram import types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import Dispatcher
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ContentType
from aiogram.utils import executor
from aiogram.utils.exceptions import MessageNotModified, RetryAfter, CantParseEntities, TelegramAPIError

from chatai import GPT
from voicing import Announcer


class TelegramBot:

    def __init__(self, config: dict, gpt, announcer):
        self.storage = MemoryStorage()
        self.bot = Bot(token=config["token_bot"])
        self.dp = Dispatcher(self.bot, storage=self.storage)
        self.in_cor = InlineKeyboardMarkup(row_width=4)
        self.button_clear = InlineKeyboardButton(text="voice", callback_data="voice")
        self.in_cor.add(self.button_clear)
        self.gpt: GPT = gpt
        self.announcer: Announcer = announcer

    async def _chat(self, message: types.Message, text: str = None, audio=False):
        """
        Функция для обработки сообщений от пользователя
        """
        if not audio:
            text = message.text
        counter = 0
        waiting = await message.reply("...")
        await self.bot.send_chat_action(message.from_user.id, "typing")
        async for i in self.gpt.create_chat(text, chat_id=str(message.from_user.id)):
            try:
                if 'not_finished' in i and counter % 10 == 0:
                    await waiting.edit_text(i[0])
                elif isinstance(i, str):
                    await waiting.edit_text(i, reply_markup=self.in_cor, parse_mode=types.ParseMode.MARKDOWN)
            except MessageNotModified as e:
                logging.warning(e)
            except RetryAfter as e:
                logging.warning(e)
                await asyncio.sleep(e.timeout)
            except CantParseEntities as e:
                logging.warning(e)
                await waiting.edit_text(i, reply_markup=self.in_cor)
            counter += 1
            await asyncio.sleep(0.01)

    async def _gen_image(self, message: types.Message):
        logging.info(f"New prompt generate image from @{message.from_user.username} (id: {message.from_user.id})")
        prompt = message.text.replace("/image", "")

        if prompt == '':
            await message.reply("You must provide a prompt")
            return

        await self.bot.send_chat_action(message.from_user.id, "upload_photo")
        url_image = await self.gpt.generate_image(prompt)
        if not url_image.startswith("https://"):
            await message.reply(url_image)
            return
        await self.bot.send_photo(message.from_user.id, url_image)

    async def _voicing(self, callback: types.CallbackQuery):
        logging.info(
            f'Request to be converted into audio from {callback.from_user.username} (id: {callback.from_user.id})')
        await self.bot.send_chat_action(callback.from_user.id, 'record_voice')
        voices = await self.announcer.voicing(callback.message.text, callback.from_user.id)
        for voice in voices:
            if voice is None:
                await self.bot.send_message(callback.from_user.id, "Unfortunately, I can't recognize this message")
                return
            await self.bot.send_chat_action(callback.from_user.id, 'upload_voice')
            ogg_file = types.InputFile(voice)
            try:
                await self.bot.send_voice(callback.from_user.id, ogg_file)
            except TelegramAPIError as e:
                logging.warning(e)

    async def _start(self, message: types.Message):
        self.gpt.create_user_history(f'{message.from_user.id}', f'@{message.from_user.username}')
        await self.bot.send_message(message.from_user.id,
                                    f"Hi👋\n{message.from_user.first_name}, please write your question.")

    async def _clear_chat(self, message: types.Message):
        """
        Обработка кнопки Clear
        """
        logging.info(f"Clear history from @{message.from_user.username} (id: {message.from_user.id})")
        self.gpt.clear_history(chat_id=str(message.from_user.id))
        await self.bot.send_message(message.from_user.id, "History brushed off✅")

    async def _get_system_message_for_user(self, message: types.Message):
        text = message.text.replace("/system_message", "")
        self.gpt.system_message(text, chat_id=str(message.from_user.id))
        await self.bot.send_message(message.from_user.id, "Complete✅")

    async def _audio_to_chat(self, audio: types.Message):
        logging.info(f"New audio received from user @{audio.from_user.username} (id: {audio.from_user.id})")
        await audio.voice.download(destination_file=f'audio/{audio.from_user.id}.ogg')
        await self.gpt.convert_audio(chat_id=str(audio.from_user.id))
        text = await self.gpt.transcriptions(chat_id=str(audio.from_user.id))
        await self._chat(audio, text, audio=True)

    async def _message(self, message: types.Message):
        self.gpt.create_user_history(f'{message.from_user.id}', f'@{message.from_user.username}')
        logging.info(f"New message received from user @{message.from_user.username} (id: {message.from_user.id})")
        await self._chat(message)

    def _reg_handler(self, dp: Dispatcher):
        dp.register_message_handler(self._start, commands="start")
        dp.register_message_handler(self._clear_chat, commands="clear")
        dp.register_callback_query_handler(self._voicing, text="voice")
        dp.register_message_handler(self._get_system_message_for_user, commands="system_message")
        dp.register_message_handler(self._gen_image, commands="image")
        dp.register_message_handler(self._audio_to_chat, content_types=ContentType.VOICE)
        dp.register_message_handler(self._message)

    def run(self):
        self._reg_handler(self.dp)
        executor.start_polling(self.dp, skip_updates=True)

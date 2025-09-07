__version__ = (1, 0, 0)
# meta developer: @PluginIDEbot
# meta name: AutoClicker
# meta banner: https://yufic.ru/api/hc/?a=AutoClicker&b=@PluginIDEbot
# scope: hikka_only
# scope: hikka_min 1.2.10

from telethon.tl.types import Message, ReplyInlineMarkup, KeyboardButtonCallback
from telethon.tl.functions.messages import GetBotCallbackAnswerRequest
from .. import loader, utils
import logging

logger = logging.getLogger(__name__)

@loader.tds
class AutoClickerMod(loader.Module):
    """
    Позволяет автоматически нажимать на инлайн-кнопки в сообщениях.
    Поддерживает только Callback-кнопки.
    """
    strings = {
        "name": "AutoClicker",
        "usage_doc": "Автоматически нажимает на указанную инлайн-кнопку.\nИспользование: <code>.autoclick [ссылка на сообщение] [текст кнопки]</code>",
        "no_args": "<emoji document_id=5260342697075416641>❌</emoji> <b>Укажите ссылку на сообщение и текст кнопки.</b>\nПример: <code>.autoclick https://t.me/c/12345/678 Кнопка</code>",
        "invalid_link": "<emoji document_id=5260342697075416641>❌</emoji> <b>Неверная ссылка на сообщение.</b>",
        "fetching_message": "<emoji document_id=5443127283898405358>📥</emoji> <b>Получаю сообщение...</b>",
        "no_inline_keyboard": "<emoji document_id=5260342697075416641>❌</emoji> <b>В этом сообщении нет инлайн-клавиатуры.</b>",
        "button_not_found": "<emoji document_id=5260342697075416641>❌</emoji> <b>Кнопка с текстом '<code>{}</code>' не найдена в этом сообщении.</b>",
        "not_callback_button": "<emoji document_id=5260342697075416641>❌</emoji> <b>Кнопка '<code>{}</code>' не является Callback-кнопкой (поддерживаются только они).</b>",
        "clicking": "<emoji document_id=5323761960829862762>⚡</emoji> <b>Нажимаю на кнопку '<code>{}</code>'...</b>",
        "click_success": "<emoji document_id=5260726538302660868>✅</emoji> <b>Кнопка '<code>{}</code>' успешно нажата!</b>",
        "click_failed": "<emoji document_id=5260342697075416641>❌</emoji> <b>Не удалось нажать кнопку '<code>{}</code>'. Ошибка: <code>{}</code></b>",
        "error": "<emoji document_id=5260342697075416641>❌</emoji> <b>Произошла ошибка: <code>{}</code></b>",
    }

    strings_ru = {
        "usage_doc": "Автоматически нажимает на указанную инлайн-кнопку.\nИспользование: <code>.autoclick [ссылка на сообщение] [текст кнопки]</code>",
        "no_args": "<emoji document_id=5260342697075416641>❌</emoji> <b>Укажите ссылку на сообщение и текст кнопки.</b>\nПример: <code>.autoclick https://t.me/c/12345/678 Кнопка</code>",
        "invalid_link": "<emoji document_id=5260342697075416641>❌</emoji> <b>Неверная ссылка на сообщение.</b>",
        "fetching_message": "<emoji document_id=5443127283898405358>📥</emoji> <b>Получаю сообщение...</b>",
        "no_inline_keyboard": "<emoji document_id=5260342697075416641>❌</emoji> <b>В этом сообщении нет инлайн-клавиатуры.</b>",
        "button_not_found": "<emoji document_id=5260342697075416641>❌</emoji> <b>Кнопка с текстом '<code>{}</code>' не найдена в этом сообщении.</b>",
        "not_callback_button": "<emoji document_id=5260342697075416641>❌</emoji> <b>Кнопка '<code>{}</code>' не является Callback-кнопкой (поддерживаются только они).</b>",
        "clicking": "<emoji document_id=5323761960829862762>⚡</emoji> <b>Нажимаю на кнопку '<code>{}</code>'...</b>",
        "click_success": "<emoji document_id=5260726538302660868>✅</emoji> <b>Кнопка '<code>{}</code>' успешно нажата!</b>",
        "click_failed": "<emoji document_id=5260342697075416641>❌</emoji> <b>Не удалось нажать кнопку '<code>{}</code>'. Ошибка: <code>{}</code></b>",
        "error": "<emoji document_id=5260342697075416641>❌</emoji> <b>Произошла ошибка: <code>{}</code></b>",
        "_cls_doc": "Позволяет автоматически нажимать на инлайн-кнопки в сообщениях.\nПоддерживает только Callback-кнопки.",
        "_cmd_doc_autoclickcmd": "Нажать на инлайн-кнопку"
    }

    @loader.command(ru_doc="Нажать на инлайн-кнопку")
    @loader.owner
    @loader.sudo
    async def autoclickcmd(self, message: Message):
        """
        Automatically clicks a specified inline button.
        Usage: .autoclick [message_link] [button_text]
        """
        args = utils.get_args_raw(message)
        if not args:
            return await utils.answer(message, self.strings("no_args"))

        parts = args.split(' ', 1)
        if len(parts) < 2:
            return await utils.answer(message, self.strings("no_args"))

        message_link = parts[0]
        button_text = parts[1].strip()

        try:
            # utils.parse_message_link возвращает (chat_id_в_формате_Telethon, message_id)
            # Например, для t.me/c/12345/678 вернет (-100123456, 678)
            chat_id_tl, msg_id = utils.parse_message_link(message_link)
        except ValueError:
            return await utils.answer(message, self.strings("invalid_link"))

        status_message = await utils.answer(message, self.strings("fetching_message"))

        try:
            # Получаем сообщение, используя полученные chat_id и msg_id
            target_message = await self.client.get_messages(chat_id_tl, ids=msg_id)
            if not target_message:
                await utils.answer(status_message, self.strings("invalid_link"))
                return
            
            if not isinstance(target_message.reply_markup, ReplyInlineMarkup):
                await utils.answer(status_message, self.strings("no_inline_keyboard"))
                return

            target_button = None
            for row in target_message.reply_markup.rows:
                for button in row.buttons:
                    if button.text == button_text:
                        target_button = button
                        break
                if target_button:
                    break

            if not target_button:
                await utils.answer(status_message, self.strings("button_not_found").format(button_text))
                return

            if not isinstance(target_button, KeyboardButtonCallback):
                await utils.answer(status_message, self.strings("not_callback_button").format(button_text))
                return

            await utils.answer(status_message, self.strings("clicking").format(button_text))

            # Имитируем нажатие кнопки, отправляя GetBotCallbackAnswerRequest
            # Это заставит бота обработать колбэк, как будто на него нажали.
            # 'peer' для этого запроса должен быть InputPeer для чата.
            # chat_id_tl уже находится во внутреннем формате ID Telethon.
            peer_entity = await self.client.get_input_entity(chat_id_tl)

            await self.client(GetBotCallbackAnswerRequest(
                peer=peer_entity,
                msg_id=msg_id,
                data=target_button.data,
            ))
            
            await utils.answer(status_message, self.strings("click_success").format(button_text))

        except Exception as e:
            logger.exception("Error during autoclickcmd")
            await utils.answer(status_message, self.strings("click_failed").format(button_text, str(e)))
        
        # Удаляем исходное сообщение с командой, если оно было нашим
        if message.out:
            await message.delete()
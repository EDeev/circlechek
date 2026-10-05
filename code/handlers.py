import asyncio
import logging
import os
import shutil
import tempfile

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message, CallbackQuery, ContentType, InlineKeyboardButton, InlineKeyboardMarkup, FSInputFile
from aiogram.filters import Command

from scripts import Movie, process_frames
from config import WARN

router = Router()


# СТАРТОВАЯ КОМАНДА
@router.message(Command("start", "help"))
async def helps(msg: Message) -> None:
    buttons = [[InlineKeyboardButton(text="ФУНКЦИИ", callback_data="fun"),
                InlineKeyboardButton(text="АВТОР", callback_data="auth")]]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

    await msg.answer(text="<b>Кружочичек</b> — бот для обработки видео и кружочков в Телеграме. Для начала работы "
                          "вам достаточно скинуть квадратное видео не дольше минуты в чат, чтобы получить кружок. "
                          "Или скинуть кружок, выбрать формат обработки углов и получить готовый видеоролик! "
                          "<b>НО</b> у Телеграмма бывают кружочки с некорректными метаданными, из-за чего его "
                          "обработка становится невозможной, или в итоге видео будет с браком, поэтому "
                          "<b>обязательно проверяйте</b> полученный результат!", reply_markup=keyboard)


@router.callback_query(F.data == "auth")
async def author(call: CallbackQuery) -> None:
    await call.message.answer('<b>| АВТОР |</b>\n\n<b>>></b> Этот телеграм бот, крайне прост и примитивен. В его '
                              'распоряжении есть всего лишь две функции, а именно: превращение квадратных '
                              'видеороликов в кружочки и скачивание кружочков с последующей обработкой краёв в '
                              'двух предложенных вариантах.'
                                   
                              '\n\nЯ же пишу подобные небольшие проекты, о которых вы можете узнать '
                              'больше на моём <a href="https://github.com/EDeev">GitHub</a>.')


@router.callback_query(F.data == "fun")
async def function(call: CallbackQuery) -> None:
    await call.message.answer('<b>| ФУНКЦИИ |</b>\n\n<b>1.</b> Обработка кружочка с градиентным или размытым фоном на '
                              'выбор по бокам\n<b>2.</b> Получение из квадратного видео длиною не больше минуты кружочек')


# ОБРАБОТЧИК ВИДЕО
@router.message(F.content_type == ContentType.VIDEO)
async def video_to_circle(msg: Message) -> None:
    video = f"../data/circles/{msg.chat.id}_{msg.message_id}.mp4"

    await msg.reply("<b>Началась обработка видео!</b> Оно должно быть квадратным и не дольше одной минуты, в ином "
                    "случае бот в ответ вернёт вам изначальное видео, а не кружочек!")
    try:
        await msg.bot.download(file=msg.video.file_id, destination=video)
        await msg.answer_video_note(video_note=FSInputFile(video))
    except TelegramBadRequest as err:
        logging.warning("Не удалось сделать кружочек: %s", err)
        await msg.answer("<b>Не получилось сделать кружочек.</b> Видео должно быть квадратным, не дольше минуты "
                         "и не больше 20 МБ.")
    finally:
        if os.path.exists(video):
            os.remove(video)


# ОБРАБОТЧИК КРУЖОЧКОВ
@router.message(F.content_type == ContentType.VIDEO_NOTE)
async def video_note(msg: Message) -> None:
    # номер сообщения в кнопках: если прислать несколько кружочков подряд, каждый обработается свой
    buttons = [[InlineKeyboardButton(text="Градиент", callback_data=f"grad:{msg.message_id}"),
                InlineKeyboardButton(text="Блюр", callback_data=f"blur:{msg.message_id}")]]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

    msg_answer = await msg.reply("Кружочек загружается...")
    await msg.bot.download(file=msg.video_note.file_id,
                           destination=f"../data/video_notes/{msg.chat.id}_{msg.message_id}.mp4")
    await msg_answer.edit_text(text=WARN + "Какой тип фона в углах вы выберите?", reply_markup=keyboard)


@router.callback_query(F.data.regexp(r"^(grad|blur):\d+$"))
async def work_part(call: CallbackQuery) -> None:
    mode, note_id = call.data.split(":")
    video_name = f"{call.message.chat.id}_{note_id}"
    video_file = video_name + ".mp4"
    source = "../data/video_notes/" + video_file

    if not os.path.exists(source):
        # кнопку нажали повторно или кружочек уже обработан
        await call.answer("Этот кружочек уже обработан. Пришлите его ещё раз.", show_alert=True)
        return

    msg = await call.message.edit_text(WARN + "<b>Начало обработки!</b>")

    # отдельная папка на каждую обработку и уборка в любом случае — иначе после первой же ошибки
    # повторная обработка в этом чате падала на уже существующей папке
    path = tempfile.mkdtemp(prefix=video_name + "-", dir="../data/videos")
    try:
        path_video = path + "/" + video_file
        os.replace(source, path_video)

        path_frames = path + "/frames"
        os.mkdir(path_frames)

        path_background = path + "/background"
        os.mkdir(path_background)

        # тяжёлая обработка — в отдельном потоке, чтобы бот не замирал для остальных пользователей
        msg = await msg.edit_text(WARN + "<b>Этап:</b> 1 - Обработка видео.")
        video = Movie(path_video, video_name, path)
        if not await asyncio.to_thread(video.split_into_frames):
            await msg.edit_text("<b>Возникла ошибка!</b> Кружочек невозможно обработать!")
            return

        msg = await msg.edit_text(WARN + "<b>Этап:</b> 2 - Обработка кадров.")
        frames = await asyncio.to_thread(process_frames, path_frames, path_background, mode)

        msg = await msg.edit_text(WARN + "<b>Этап:</b> 3 - Объединение кадров.")
        result = await asyncio.to_thread(video.unity_into_video, frames)

        msg_final = await msg.edit_text(WARN + "<b>Готово!</b> Видео отправляется...")

        reply_to = call.message.reply_to_message
        await msg.answer_video(video=FSInputFile(result), caption=WARN,
                               reply_to_message_id=reply_to.message_id if reply_to else None)
        await msg_final.delete()
    except Exception:
        logging.exception("Ошибка обработки кружочка")
        await msg.edit_text("<b>Возникла ошибка!</b> Кружочек невозможно обработать!")
    finally:
        shutil.rmtree(path, ignore_errors=True)

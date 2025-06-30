from aiogram import types, F, Router
from aiogram.types import Message, CallbackQuery, ContentType, InlineKeyboardButton, InlineKeyboardMarkup, FSInputFile
from aiogram.filters import Command

import shutil

from scripts import *
from config import WARN

router = Router()


# СТАРТОВАЯ КОМАНДА
@router.message(Command("start", "help"))
async def helps(msg: Message) -> None:
    buttons = [[InlineKeyboardButton(text="ФУНКЦИИ", callback_data="fun"),
                InlineKeyboardButton(text="АВТОР", callback_data="auth")]]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons, row_width=2)

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
                              'больше на моём <a href="https://github.com/IGlek">GitHub</a>.')


@router.callback_query(F.data == "fun")
async def function(call: CallbackQuery) -> None:
    await call.message.answer('<b>| ФУНКЦИИ |</b>\n\n<b>1.</b> Обработка кружочка с градиентным или размытым фоном на '
                              'выбор по бокам\n<b>2.</b> Получение из квадратного видео длиною не больше минуты кружочек')


# ОБРАБОТЧИК ВИДЕО
@router.message(F.content_type == ContentType.VIDEO)
async def video_to_circle(msg: Message) -> None:
    video = "../data/circles/" + str(msg.chat.id) + ".mp4"

    await msg.reply("<b>Началась обработка видео!</b> Оно должно быть квадратным и не дольше одной минуты, в ином "
                    "случае бот в ответ вернёт вам изначальное видео, а не кружочек!")
    await msg.bot.download(file=msg.video.file_id, destination=video)
    await msg.answer_video_note(video_note=FSInputFile(video))
    os.remove(video)


# ОБРАБОТЧИК КРУЖОЧКОВ
@router.message(F.content_type == ContentType.VIDEO_NOTE)
async def video_note(msg: Message) -> None:
    buttons = [[InlineKeyboardButton(text="Градиент", callback_data="grad"),
                InlineKeyboardButton(text="Блюр", callback_data="blur")]]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons, row_width=2)

    msg_answer = await msg.reply("Кружочек загружается...")
    await msg.bot.download(file=msg.video_note.file_id, destination="../data/video_notes/" + str(msg.chat.id) + ".mp4")
    await msg_answer.edit_text(text=WARN + "Какой тип фона в углах вы выберите?", reply_markup=keyboard)


@router.callback_query(lambda call: call.data == "grad" or call.data == "blur")
async def work_part(call: CallbackQuery) -> None:
    msg = await call.message.edit_text(WARN + "<b>Начало обработки!</b>")

    video_name = str(msg.chat.id)
    video_file = video_name + ".mp4"

    path = f"../data/videos/{video_name}"
    os.mkdir(path)

    path_video = path + "/" + video_file
    os.replace("../data/video_notes/" + video_file, path_video)

    path_frames = path + f"/frames"
    os.mkdir(path_frames)

    path_background = path + f"/background"
    os.mkdir(path_background)

    msg = await msg.edit_text(WARN + "<b>Этап:</b> 1 - Обработка видео.")
    video = Movie(path_video, video_name, path)
    procces = video.split_into_frames()

    if not procces:
        await msg.edit_text("<b>Возникла ошибка!</b> Кружочек невозможно обработать!")
        shutil.rmtree(path)
        return

    msg = await msg.edit_text(WARN + "<b>Этап:</b> 2 - Обработка кадров.")
    frames = list(sorted(os.listdir(path_frames)))

    for frame in frames:
        img = Frame(path_frames + "/" + frame, path_background + "/" + f'{frame[:-5]}-g.jpeg')
        width, height = img.size()

        if call.data == "blur":
            img.blur(width, height)
        else:
            r, g, b = img.medium_color(); nearly = 10
            img.gradient(width, height, (r - nearly, g - nearly, b - nearly),
                         (r + nearly, g + nearly, b + nearly), (True, False, False))

        img.unity_image()

    msg = await msg.edit_text(WARN + "<b>Этап:</b> 3 - Объединение кадров.")
    video.unity_into_video(frames)

    msg_final = await msg.edit_text(WARN + "<b>Готово!</b> Видео отправляется...")

    await msg.answer_video(video=FSInputFile(path + "/acs-" + video_file), caption=WARN,
                           reply_to_message_id=call.message.reply_to_message.message_id)
    await msg_final.delete()

    shutil.rmtree(path)

from dataclasses import dataclass
import logging
#скачано
from aiogram import Bot, Dispatcher, executor, types
#конфиги
from cfg import api_key
#наш собственный "драйвер" бд
import db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

# Initialize bot and dispatcher
bot = Bot(token=api_key)
dp = Dispatcher(bot)


@dataclass
class Texts:
    """
    Датакласс со всеми репликами бота
    """
    start_message = "Привет, я бот to-do list.\n" \
                    "Я помогу тебе не забывать о задачах.\n" \
                    "Ты можешь создавать задачи, переносить в выполненные или вовсе удалять."
    help_message = "/help - подсказка по пользованию ботом\n" \
                   "/new - добавить новую задачу, например: \n" \
                   ">>> /new Сделать проект\n" \
                   "/in_progress - показывает задачи которые находятся в процессе выполнения\n" \
                   "/ready - перемещает задачу с определённым номером в выполненные, например: \n" \
                   ">>> /ready 17\n" \
                   "/get_ready - показывает готовые задачи\n" \
                   "/delete - удаляет задачу под определённым номером, например\n" \
                   ">>> /delete 17\n"
    user_not_exists = "Такого пользователя не существует"
    added = "Задача добавлена"
    deleted = "Задача удалена"
    ready = "Задача перенесена в список выполненных"
    empty = "Список пустой"
    error = "Что-то пошло не так, прочитай инструкции в /help"


@dp.message_handler(commands='start')
async def start_cmd_handler(message: types.Message):
    """
    Начинает диалог с пользователем
    (если пользователь ни разу не прописал /start,
    бот не имеет возможности писать пользователю)
    """
    _id = message.from_user.id
    await db.create_new_user(_id)
    await message.answer(text=Texts.start_message)
    await send_help(_id)
    logger.debug(f"{_id} - <start>")


@dp.message_handler(commands='help')
async def help_cmd_handler(message: types.Message):
    """
    Вызывает функцию send_help для отправки определённому пользователю сообщения с подсказками
    """
    await send_help(message.from_user.id)


async def send_help(_id: int):
    """
    Выводит help-info по взаимодействию с ботомд0
    :param _id: id пользователя
    :type _id: int
    """
    await bot.send_message(chat_id=_id, text=Texts.help_message)


@dp.message_handler(commands='new')
async def new_cmd_handler(message: types.Message):
    _id = message.from_user.id
    task = message.text.replace("/new", "").strip()
    if len(task)==0:
        await bot.send_message(_id, Texts.error)
    elif await db.add_item(_id, task) == 0:
        logger.error(f"{_id} can\'t add")
        await bot.send_message(_id, Texts.user_not_exists)
    else:
        await bot.send_message(_id, Texts.added)


@dp.message_handler(commands='in_progress')
async def in_progress_cmd_handler(message: types.Message):
    _id = message.from_user.id
    if (var := await db.get_in_progress(_id)) != 0:
        if len(var) > 0:
            message = "Список дел:\n" + "\n".join(f"{i + 1}) {task}" for i, task in enumerate(var))
            await bot.send_message(_id, message)
        else:
            await bot.send_message(_id, Texts.empty)
    else:
        logger.error(f"{_id} not exists in progress")
        await bot.send_message(_id, Texts.user_not_exists)


@dp.message_handler(commands='ready')
async def ready_cmd_handler(message: types.Message, ):
    _id = message.from_user.id
    n = message.text.replace("/ready", "").strip()
    if n.isdigit() is not True:
        await bot.send_message(_id, Texts.error)
    if await db.to_ready(_id, int(n)) == 0:
        logger.error(f"{_id} can\'t ready")
        await bot.send_message(_id, Texts.user_not_exists)
    else:
        await bot.send_message(_id, Texts.ready)


@dp.message_handler(commands='get_ready')
async def get_ready_cmd_handler(message: types.Message):
    _id = message.from_user.id
    if (var := await db.get_ready(_id)) != 0:
        if len(var) > 0:
            message = "Список завершённых дел\n" + "\n".join(f"{i + 1}) {task}" for i, task in enumerate(var))
            await bot.send_message(_id, message)
        else:
            await bot.send_message(_id, Texts.empty)
    else:
        logger.error(f"{_id} not exists in progress")
        await bot.send_message(_id, Texts.user_not_exists)


@dp.message_handler(commands='delete')
async def delete_cmd_handler(message: types.Message):
    _id = message.from_user.id
    n = message.text.replace("/delete", "").strip()
    if await db.delete(_id, int(n)) == 0:
        logger.error(f"{_id} can\'t remove")
        await bot.send_message(_id, Texts.user_not_exists)
    else:
        await bot.send_message(_id, Texts.ready)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

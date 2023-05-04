from operator import call
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.types import Message, CallbackQuery, ContentType


from data.config import ADMINS, CHANNELS
from keyboards.inline.manage_post import confirmation_keyboard, post_callback
from loader import bot, dp
from states.newpost import NewPost


@dp.message_handler(Command("post"))
async def create_post(message: types.Message):
    await message.answer("Chop etish uchun post yuboring. ")
    await NewPost.NewMessage.set()


@dp.message_handler(state=NewPost.NewMessage, content_types=ContentType.ANY)
async def enter_message(message: Message, state: FSMContext):

    photo_obj = message.photo[2]

    text = message.caption

    file_id = photo_obj.file_id
    width = photo_obj.width
    height = photo_obj.height

    print(f"image size {width}x{height}")
    if width == height == 640:
        await message.answer("rasm o'lchami togri keldi")

    if width and height == 640:
        await bot.send_photo(chat_id='-1001801973705', photo=file_id, caption=text) # noqa
    else:
        await message.answer("640x640 o'lchamli rasm yuboring."),
        await call.answer("Post rad etildi.", show_alert=True)
        await call.message.edit_reply_markup()

    await state.update_data(
        text=message.html_text,
        metion=message.from_user.get_mention(),
        file_id=file_id
    )
    await message.answer(f"Postni tekshirish uchun yuboraymi?",  reply_markup=confirmation_keyboard) # noqa
    await NewPost.next()


@dp.callback_query_handler(post_callback.filter(action="post"), state=NewPost.Confirm) # noqa
async def confirm_post(call: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        mention = data.get("mention")
        text = data.get("text")
        file_id = data.get("file_id")

    await state.finish()
    await call.message.edit_reply_markup()
    await bot.send_message(chat_id=call.from_user.id, text='Post Adminga yuborldi') # noqa
    await bot.send_message(ADMINS[0], f"Foydalanuvchi {mention} quyidagi postni chop etmoqchi:") # noqa
    await bot.send_photo(
        chat_id=ADMINS[0],
        photo=file_id,
        caption=text,
        reply_markup=confirmation_keyboard,
    )


@dp.callback_query_handler(post_callback.filter(action="cancel"), state=NewPost.Confirm) # noqa
async def cancel_post(call: CallbackQuery, state: FSMContext):
    await state.finish()
    await call.message.edit_reply_markup()
    await call.message.answer("Post rad etildi.")


@dp.message_handler(state=NewPost.Confirm)
async def post_unknown(message: Message):
    await message.answer("Chop etish yoki rad etishni tanlang")


@dp.callback_query_handler(post_callback.filter(action="post"), user_id=ADMINS)
async def approve_post(call: CallbackQuery):
    await call.answer("Chop etishga ruhsat berdingiz.", show_alert=True)
    target_channel = CHANNELS[0]
    message = await call.message.edit_reply_markup()
    await message.send_copy(chat_id=target_channel)


@dp.callback_query_handler(post_callback.filter(action="cancel"), user_id=ADMINS) # noqa
async def decline_post(call: CallbackQuery):
    await call.answer("Post rad etildi.", show_alert=True)
    await call.message.edit_reply_markup()

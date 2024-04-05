import datetime
from app.utils.order_receipt import create_assembly_pdf, create_order_pdf
import config
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, BufferedInputFile
from aiogram.filters import StateFilter, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state

from app.FSM.fsm import Collecting_the_cake
from app.requests.cake_assemly_requests import collecting_cake

from app.keyboards.reply_rb import user_menu_kb
from app.keyboards.inline_kb import new_user, generate_calendar_markup

cake = Router()

@cake.message(Command(commands='cancel'), StateFilter(default_state))
async def process_cancel_command(message: Message):
    await message.answer(
        text='Вы не заполняете форму, поэтому невозможно воспользоваться данной командой!'
    )

@cake.message(Command(commands='cancel'), ~StateFilter(default_state))
async def process_cancel_command_state(message: Message, state: FSMContext):
    await message.answer(
        text='Отмена заполнения формы\n\nПри необходимости заполните форму заново'
    )
    await state.clear()

@cake.message(F.text.endswith('Собрать свой торт'), StateFilter(default_state))
async def cake_collection(message: Message, state: FSMContext):
    await message.answer('Магазин <b>"ВКУСНЫЕ ТОРТЫ"</b> предоставляет услугу по собору своего торта\n\nДля реализации задуманного укажите событие, к которому требуется подготовить торт\n\n❌ Отмена - /cancel')
    await state.set_state(Collecting_the_cake.event)

@cake.message(StateFilter(Collecting_the_cake.event))
async def process_event(message: Message, state: FSMContext):
    await state.update_data(event=message.text)
    await message.answer('Далее нам от Вас потребуется описание торта, по параметрам:\n\nВес (в кг.) -\nКоличество уровней (1, 2 ...) -\nФормы каждого уровня (Прямоугольник, круг, сердце, <i>Ваш вариант</i>) -\nЦвет глазури -\nНачинка (бисквит и т.д.) -\nНадпись на торте (при необходимости)\nТакже можете указать любые Ваши пожелания\n\n❌ Отмена - /cancel')
    await state.set_state(Collecting_the_cake.description)

@cake.message(StateFilter(Collecting_the_cake.description))
async def process_descriphion(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer('Загрузите 📷 фото примерного торта, который Вам необходим\n\nПропустить добавление фото - /skip\n\n❌ Отмена - /cancel')
    await state.set_state(Collecting_the_cake.image)

@cake.message(Command(commands='skip'))
async def process_skip(message: Message, state: FSMContext):
        # Если получена команда "/skip", просто переходим к следующему шагу без сохранения фотографии
        await state.update_data(image=None)
        now = datetime.datetime.now()
        current_year = now.year
        current_month = now.month
        current_date = now.date()
        await state.set_state(Collecting_the_cake.data)
        await message.answer("Пропускаем добавление фотографии. Укажите дату торжества.", reply_markup=await generate_calendar_markup (current_year, current_month, current_date))  

@cake.message(StateFilter(Collecting_the_cake.image) or Command(commands='skip'))
async def process_image(message: Message, state: FSMContext):  
        # Если получено фото, сохраняем его и переходим к следующему шагу
        await state.update_data(image=message.photo[-1].file_id)
        now = datetime.datetime.now()
        current_year = now.year
        current_month = now.month
        current_date = now.date()
        await state.set_state(Collecting_the_cake.data)
        await message.answer("Фотография успешно добавлена. Укажите дату торжества.", reply_markup=await generate_calendar_markup (current_year, current_month, current_date))
     

@cake.callback_query(F.data.startswith('calendar'))
async def process_calendar_callback(callback: CallbackQuery):
    _, year, month = callback.data.split("_")
    if 0 < int(month) < 13:
        current_date = datetime.datetime.now().date()
        markup = await generate_calendar_markup(int(year), int(month), current_date)

        await callback.bot.edit_message_reply_markup(chat_id=callback.message.chat.id,
                                        message_id=callback.message.message_id,
                                        reply_markup=markup)
    else:
        await callback.answer('Вы пытаетесь выйти за пределы текущего года!')


@cake.callback_query(F.data.startswith('day'), StateFilter(Collecting_the_cake.data))
async def process_day_callback(callback: CallbackQuery, state: FSMContext):
    day = callback.data.split('_')[0][-1] 
    day_day = callback.data.split('_')[-1] 
    if day != '🔒' and day_day != ' ':
        _, year, month, day = callback.data.split("_")
        selected_date = f"{day}.{month}.{year}"
        await state.update_data({'data':selected_date})
        await callback.answer(f'Дата доставки установлена на {selected_date}. Спасибо!', show_alert=True)
        await callback.message.delete()
        total = await state.get_data()


        if await collecting_cake(total, callback.from_user.id):
            if not total["image"] == None:
                await callback.message.answer_photo(total['image'], caption=f"<b><i>Событие:</i></b> {total['event']}   \n\n<b><i>Описание:</i></b> {total['description']}\n\n<b><i>Дата готовности:</i></b> {total['data']}")
                await callback.message.bot.send_photo(chat_id=config.ADMIN_ID, photo=total['image'], caption=f"<b><i>Событие:</i></b>   {total['event']}\n\n<b><i>Описание:</i></b> {total['description']}\n\n<b><i>Дата готовности:</i></b> {total['data']}",        reply_markup=await new_user(callback.from_user.id, callback.from_user.first_name))
            else:
                await callback.message.answer(f"<b><i>Событие:</i></b> {total['event']}   \n\n<b><i>Описание:</i></b> {total['description']}\n\n<b><i>Дата готовности:</i></b> {total['data']}")
                await callback.message.bot.send_message(chat_id=config.ADMIN_ID, text=f"<b><i>Событие:</i></b>   {total['event']}\n\n<b><i>Описание:</i></b> {total['description']}\n\n<b><i>Дата готовности:</i></b> {total['data']}",        reply_markup=await new_user(callback.from_user.id, callback.from_user.first_name))
            await state.clear()
            await callback.message.answer('✅ Ваш заказ успешно отправлен администратору на рассмотрение и оценку 💵 стоимости',        reply_markup=await user_menu_kb())
            pdf_file = await create_assembly_pdf(callback.from_user.first_name, total)
            await callback.bot.send_document(chat_id=config.ADMIN_ID, document=BufferedInputFile(pdf_file, filename=f"Сборка_{callback.from_user.first_name}.pdf"))
        else:
            await callback.message.answer('❌ Произошла ошибка при отправке заказа', reply_markup=await user_menu_kb())
            await state.clear()
    else:
        await callback.answer('Данную дату нельзя выбрать')



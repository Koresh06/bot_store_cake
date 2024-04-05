import datetime
import config
from aiogram import Router, F, types
from aiogram.types import Message, CallbackQuery, ContentType, ReplyKeyboardRemove
from aiogram.filters import StateFilter, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state

from app.keyboards.inline_kb import generate_calendar_markup, order_method_kb, ordering_solution
from app.FSM.fsm import OrderPlacement
from app.requests.order_placement_requests import (
    payment_cart,
    product_name_desc_price,
    adding_order_information,
    id_order_user,
    retrieve_data,
    payment_confirmation,

)
from app.requests.basket_user_requests import clear_cart_pr
from app.keyboards.reply_rb import user_menu_kb

payment = Router()

@payment.message(Command(commands='cancel'), StateFilter(default_state))
async def process_cancel_command(message: Message):
    await message.answer(
        text='Вы не заполняете форму, поэтому невозможно воспользоваться данной командой!'
    )

@payment.message(Command(commands='cancel'), ~StateFilter(default_state))
async def process_cancel_command_state(message: Message, state: FSMContext):
    await message.answer(
        text='Отмена заполнения формы\n\nПри необходимости заполните форму заново'
    )
    await state.clear()

@payment.message(F.text.endswith('Оформить заказ'), StateFilter(default_state))
async def process_payment(message: Message, state: FSMContext):
    now = datetime.datetime.now()
    current_year = now.year
    current_month = now.month
    current_date = now.date()
    await message.answer('🗓 Укажите дату торжества, к которой необходим торт', reply_markup=await generate_calendar_markup(current_year, current_month, current_date))
    await state.set_state(OrderPlacement.data)

@payment.callback_query(F.data.startswith('calendar'))
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

@payment.callback_query(F.data.startswith('day🔒'))
@payment.callback_query(F.data.startswith('day'), StateFilter(OrderPlacement.data))
async def process_day_callback(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    day = callback.data.split('_')[0][-1] 
    day_day = callback.data.split('_')[-1] 
    if day != '🔒' and day_day != ' ':
        _, year, month, day = callback.data.split("_")
        selected_date = f"{day}.{month}.{year}"
        await state.update_data({'data':selected_date})
        await callback.answer(f'Дата доставки установлена на {selected_date}. Спасибо!', show_alert=True)
        await callback.message.answer('Укажите способ оплаты при получении заказа:', reply_markup=order_method_kb)
        await state.set_state(OrderPlacement.method)
    else:
        await callback.answer('Данную дату нельзя выбрать')

@payment.callback_query(F.data.startswith('method'), StateFilter(OrderPlacement.method))
async def process_method_callback(callback: CallbackQuery, state: FSMContext):
        await callback.message.delete()
        method = callback.data.split('_')[-1]
        await state.update_data({'method':method})
        result = await state.get_data()
        order = await payment_cart(callback.from_user.id)
        content = [await product_name_desc_price(item[0]) for item in order]
        killo = [item[1] for item in order]
        _price = [item[0][1] for item in content]
        name_prod = [item[0][0] for item in content]
        desc_name_killo = dict(zip(name_prod, killo))
        total_cost = sum([float(i * killo[idx])  for idx, i in enumerate(_price)])
        if await adding_order_information(callback.from_user.id, desc_name_killo, method, result['data'], total_cost):
            await callback.message.answer('Заказ оформлен!', reply_markup=ReplyKeyboardRemove())
            await clear_cart_pr(callback.from_user.id)
            await state.clear()

            id_order = await id_order_user(callback.from_user.id)
            index = id_order.all()[-1][0]
            info = await retrieve_data(index)
            order_info = info[0]
            pos = '\n'.join([f'{k}: {v} шт.' for k, v in order_info[2].items()])
            await callback. message.answer('✅ Товар оформлен!\n\nОжидайте... Адинистратор с Вами свяжеться', reply_markup=await user_menu_kb())

            await callback.message.bot.send_message(chat_id=config.ADMIN_ID, text=f'Новый заказ № {order_info[0]} от {callback.from_user.first_name}\n\nДата готовности: {order_info[1]}\n\nПозиции: {pos}\n\n💸 ОБЩАЯ СТОИМОСТЬ: {order_info[3]} RUB\n\n♻️ ОПЛАТА: {"💳 Карта" if order_info[4] == "cart" else "💵 Наличка"}', reply_markup=await ordering_solution(index, callback.from_user.id))
        else:
            await callback.message.answer('Произошла ошибка обратитесь к администратору')
            await state.clear()

    

    


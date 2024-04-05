from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from app.requests.order_user_requests import (
    get_inform_order,
    history_get_inform_order,
    get_inform_assembly,
    delete_sborka,
    history_get_inform_assembly
)
from app.keyboards.inline_kb import (
    user_orders_list,
    settings_order,
    order_nomer_user,
    nomer_assembly,
    cancellation_sborka,
    subcategories_stories,
    cancellation_history
)

from app.requests.admin_requests import delete_orders
import config

order = Router()

@order.message(F.text.endswith('Мои заказы'))
async def cmd_order_user_list(message: Message):
    await message.answer('Меню заказов', reply_markup= await user_orders_list(message.from_user.id))

@order.callback_query(F.data == 'orders_progress')
async def nomer_zak(callback: CallbackQuery):
    await callback.message.edit_text('Заказы в работе', reply_markup=await order_nomer_user(callback.from_user.id))

@order.callback_query(F.data.startswith('nomer_zak'))
async def process_order_progress(callback: CallbackQuery):
    index = int(callback.data.split('_')[-1])
    orders_user = await get_inform_order(index)
    item = orders_user[0]
    position = '\n'.join([f'{k}: {v} шт.' for k, v in item[3].items()])
    await callback.message.edit_text(f'Заказ № {item[0]}\n\nДата готовности: {item[1]}\n\nПозиции: {position}\n\nПрайс: {item[4]}\n\nОПЛАТА: {"💳 Карта" if item[2] == "cart" else "💵 Наличка"}', reply_markup=await settings_order(int(item[0])))
    await callback.answer()

@order.callback_query(F.data.startswith('cancellation_order'))
async def cancellation_order(callback: CallbackQuery):
    index = int(callback.data.split('_')[-1])
    if await delete_orders(index):
        await callback.message.delete()
        await callback.answer('Заказ отменен')
        await callback.bot.send_message(chat_id=config.ADMIN_ID, text=f'Пользователь {callback.from_user.first_name} отменил заказ № {index}')
    else:
        await callback.message.answer('Ошибка, обратитесь к администратору')

@order.callback_query(F.data == 'backward_user')
async def bak_user(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer('Меню заказов', reply_markup= await user_orders_list(callback.from_user.id))

@order.callback_query(F.data.startswith('cake_assembly'))
async def process_cake_assembly(callback: CallbackQuery):
    await callback.message.edit_text('Сборки тортов', reply_markup=await nomer_assembly(callback.from_user.id))

@order.callback_query(F.data.startswith('nomer_assem'))
async def process_inform_assembly(callback: CallbackQuery):
    await callback.message.delete()
    index = int(callback.data.split('_')[-1])
    inform_assembly = await get_inform_assembly(index)
    sborka = inform_assembly[0]
    if not sborka[2] == None:
        await callback.message.answer_photo(photo=sborka[2], caption=f"<b><i>Событие:</i></b> {sborka[1]}\n\n<b><i>Описание:</i></b> {sborka[3]}\n\n<b><i>Дата готовности:</i></b> {sborka[4]}", reply_markup=await cancellation_sborka(index))
    else:
        await callback.message.answer(f"<b><i>Событие:</i></b> {sborka[1]}\n\n<b><i>Описание:</i></b> {sborka[3]}\n\n<b><i>Дата готовности:</i></b> {sborka[4]}", reply_markup=await cancellation_sborka(index))

@order.callback_query(F.data.startswith('cancellation_sborka'))
async def process_delete_sborka(callback: CallbackQuery):
    index = int(callback.data.split('_')[-1])
    if await delete_sborka(index):
        await callback.message.delete()
        await callback.answer('Сборка торта отменена', show_alert=True)
        await callback.bot.send_message(chat_id=config.ADMIN_ID, text=f'Пользователь {callback.from_user.first_name} отменил сборку № {index}')
    else:
        await callback.message.answer('Ошибка, обратитесь к администратору')

@order.callback_query(F.data == 'user_history')
async def user_history_orders(callback: CallbackQuery):
    await callback.message.edit_text('Подкатегории:', reply_markup=await subcategories_stories(callback.from_user.id))
    
@order.callback_query(F.data == 'history_catalog')
async def process_history_catalog(callback: CallbackQuery):
    await callback.message.delete()
    history = await history_get_inform_order(callback.from_user.id)
    for item in history:
       position = '\n'.join([f'{k}: {v} шт.' for k, v in item[3].items()])
       await callback.message.answer(f'Заказ № {item[0]}\n\nДата готовности: {item[1]}\n\nПозиции: {position}\n\nПрайс: {item[4]}\n\nОПЛАТА: {"💳 Карта" if item[2] == "cart" else "💵 Наличка"}')
    await callback.message.answer('Вернуться к моим заказам!', reply_markup=cancellation_history)
    
@order.callback_query(F.data == 'history_assembly')
async def process_history_assemby(callback: CallbackQuery):
    await callback.message.delete()
    history = await history_get_inform_assembly(callback.from_user.id)
    for sborka in history:
        await callback.message.answer_photo(photo=sborka[2], caption=f"<b><i>Событие:</i></b> {sborka[1]}\n\n<b><i>Описание:</i></b> {sborka[3]}\n\n<b><i>Дата готовности:</i></b> {sborka[4]}")
    await callback.message.answer('Вернуться к Моим заказам!', reply_markup=cancellation_history)
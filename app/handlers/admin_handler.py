from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, BufferedInputFile
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state

from app.middlewares.middleware import Is_Admin
from app.FSM.fsm import Add_categories ,Update_product
from app.filters.filter import IsDigitFilter, CheckImageFilter
from app.requests.admin_requests import (
    output_categories,
    add_categories,
    add_product_db,
    delete_orders,
    users,
    get_info_admin_order,
    readiness_order,
    get_inform_assembly_admin,
    readiness_sborka,
    delete_sborka,
    admin_history_get_inform_order,
    admin_history_get_inform_assembly
)
from app.keyboards.inline_kb import (
    non_categor,
    categories,
    users_inline_buttons,
    admin_order,
    admin_catalog_order_nomer,
    user_order_availability,
    admin_catalog_sborka_nomer,
    user_sborka_availability,
    admin_subcategories_stories,
    admin_cancellation_history
)
from app.keyboards.reply_rb import admin_menu_kb
from app.requests.order_placement_requests import retrieve_data
from app.utils.order_receipt import create_order_pdf
from config import ADMIN_ID


admin = Router()

admin.message.middleware(Is_Admin())

@admin.message(Command('admin'), StateFilter(default_state))
async def cmd_admin(message: Message):
    await message.answer('Привет хозяин', reply_markup=await admin_menu_kb())

@admin.message(Command(commands='cancel'), ~StateFilter(default_state))
async def process_cancel_command_state(message: Message, state: FSMContext):
    await message.answer(
        text='🚫 Отмена заполнения формы\n\nПри необходимости заполните форму заново'
    )
    # Сбрасываем состояние и очищаем данные, полученные внутри состояний
    await state.clear()

@admin.message(F.text.endswith('Добавить товар'))
async def cmd_add_product(message: Message):
    if await output_categories():
        await message.answer('Категории', reply_markup=await categories())
    else:
        await message.answer('Каталог категорий пуст, для добавления нажмите ⬇️', reply_markup=non_categor)

@admin.callback_query(F.data == 'add_categor', StateFilter(default_state))
async def but_add_categ(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer('Введите название категории:\n\n❌ Отмена - /cancel')
    await state.set_state(Add_categories.name)
    await callback.answer()

@admin.message(StateFilter(Add_categories.name))
async def cmd_categ_name(message: Message, state: FSMContext):
    data = await state.update_data(name=message.text)
    if await add_categories(data['name']):
        await message.answer('✅ Категория добавлена успешно')
        await state.clear()
    else:
        await message.answer('🚫 Данная категория уже была добавлена', reply_markup=await admin_menu_kb())
        await state.clear()

@admin.callback_query(F.data.startswith('categ_'), StateFilter(default_state))
async def product_categ(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer('🍰 Введите название товара:\n\n❌ Отмена - /cancel')
    await state.set_state(Update_product.name)
    await state.update_data(id_categ=int(callback.data[-1]))
    await callback.answer()

@admin.message(StateFilter(Update_product.name))
async def cmd_name_product(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer('📷 Загрузите изображение товара:\n\n❌ Отмена - /cancel')
    await state.set_state(Update_product.image)

@admin.message(StateFilter(Update_product.image), CheckImageFilter())
async def cmd_image_product(message: Message, state: FSMContext):
    await state.update_data(image=message.photo[-1].file_id)
    await message.answer('🔖 Введите описание товара:\n\n❌ Отмена - /cancel')
    await state.set_state(Update_product.description)

@admin.message(StateFilter(Update_product.description))
async def cmd_description_product(messsage: Message, state: FSMContext):
    await state.update_data(description=messsage.text)
    await messsage.answer('💵 Введите прайс/цену товара:\n\n❌ Отмена - /cancel')
    await state.set_state(Update_product.price)

@admin.message(StateFilter(Update_product.price), IsDigitFilter())
async def cmd_price_product(message: Message, state: FSMContext):
    await state.update_data(price=message.text)
    product = await state.get_data()
    await message.answer_photo(product['image'])
    await message.answer(f"🍰 <b><i>Наименование:</i></b> {product['name']}\n\n🔖 <b><i>Состав/описание торта:</i></b> {product['description']}\n\n💵 <b><i>Прайс:</i></b> {product['price']} RUB")
    if await add_product_db(message.from_user.id, product):
        await message.answer('✅ Товар успешно добавлен', reply_markup=await admin_menu_kb())
        await state.clear()
    else:
        await message.answer('❌ Произошла ошибка')
        await state.clear()

@admin.callback_query(F.data.startswith('readiness'))
async def readiness_cmd(callback: CallbackQuery):
    index = int(callback.data.split('_')[-2])
    tg_id = int(callback.data.split('_')[-1])
    order = await retrieve_data(index)
    pdf_file = await create_order_pdf(callback.from_user.first_name, order)
    await callback.bot.send_document(chat_id=ADMIN_ID, document=BufferedInputFile(pdf_file, filename=f"Заказ_{index}.pdf"))
    await callback.bot.send_message(chat_id=tg_id, text=f'Администратор подтвердил ваш заказ № {index}')
    await callback.message.delete()
    await callback.answer()

@admin.callback_query(F.data.startswith('sborka_otmena'))
@admin.callback_query(F.data.startswith('order_otmena'))
@admin.callback_query(F.data.startswith('del_'))
async def delete_order_cmd(callback: CallbackQuery):
    index = int(callback.data.split('_')[-2])
    tg_id = int(callback.data.split('_')[-1])
    if callback.data.split('_')[0] == 'sborka':
        await delete_sborka(index)
        await callback.message.delete()
        await callback.answer('Сборка оклонена!')
        await callback.message.bot.send_message(chat_id=tg_id, text=f'Ваша сборка № {index} отклонена администратором')
    else:
        await delete_orders(index)
        await callback.message.delete()
        await callback.answer('Заказ оклонен!')
        await callback.message.bot.send_message(chat_id=tg_id, text=f'Ваш заказ № {index} откланен администратором')
    if callback.data.split('_')[0] == 'order' or 'sborka':
        await callback.message.answer('Заказы покупателей ->', reply_markup=await admin_order())


@admin.message(F.text.endswith('Пользователи'))
async def settings_admin(message: Message):
    if await users():
        await message.answer(text='👑 Пользователи', reply_markup=await users_inline_buttons())
    else:
        await message.answer('Пользователи отсутствуют')

@admin.message(F.text.endswith('Заказы'))
async def process_admin_order(message: Message):
    await message.answer('Заказы покупателей ->', reply_markup=await admin_order())

@admin.callback_query(F.data == 'order_catalog_admin')
async def process_catalog_orders_users(callback: CallbackQuery):
    await callback.message.edit_text('Заказы находящиеся в работе', reply_markup=await admin_catalog_order_nomer())

@admin.callback_query(F.data.startswith('id'))
async def process_info_admin_cake(callback: CallbackQuery):
    tg_id = int(callback.data.split('_')[-1])
    index = int(callback.data.split('_')[-2])
    content = await get_info_admin_order(index)
    item = content[0]
    position = '\n'.join([f'{k}: {v} шт.' for k, v in item[3].items()])
    await callback.message.edit_text(f'Заказ № {item[0]}\n\nДата готовности: {item[1]}\n\nПозиции: {position}\n\nПрайс: {item[4]}\n\nОПЛАТА: {"💳 Карта" if item[2] == "cart" else "💵 Наличка"}', reply_markup=await user_order_availability(tg_id, index))

@admin.callback_query(F.data.startswith('order_gotov'))
async def process_order_gotov(callback: CallbackQuery):
    tg_id = int(callback.data.split('_')[-1])
    index = int(callback.data.split('_')[-2])
    if await readiness_order(index):
        await callback.message.delete()
        await callback.answer(f'Подтверждение заказа № {index} о готовности')
        await callback.bot.send_message(chat_id=tg_id, text=f'Ваш заказ № {index} приготовлен!', reply_markup=await admin_order())

@admin.callback_query(F.data == 'admin_nazad')
async def process_backward_admin(callback: CallbackQuery):
    await callback.message.edit_text('Заказы покупателей ->', reply_markup=await admin_order())
        
@admin.callback_query(F.data == 'cake_collection_admin')
async def process_cake_assembly(callback: CallbackQuery):
    await callback.message.edit_text('Сборки тортов', reply_markup=await admin_catalog_sborka_nomer())

@admin.callback_query(F.data.startswith('sborka/id'))
async def process_inform_assembly(callback: CallbackQuery):
    await callback.message.delete()
    tg_id = int(callback.data.split('_')[-1])
    index = int(callback.data.split('_')[-2])
    inform_assembly = await get_inform_assembly_admin(index)
    sborka = inform_assembly[0]
    if not sborka[2] == None:
        await callback.message.answer_photo(photo=sborka[2], caption=f"<b><i>Событие:</i></b> {sborka[1]}\n\n<b><i>Описание:</i></b> {sborka[3]}\n\n<b><i>Дата готовности:</i></b> {sborka[4]}", reply_markup=await user_sborka_availability(tg_id, index))
    else:
        await callback.message.answer(f"<b><i>Событие:</i></b> {sborka[1]}\n\n<b><i>Описание:</i></b> {sborka[3]}\n\n<b><i>Дата готовности:</i></b> {sborka[4]}", reply_markup=await user_sborka_availability(tg_id, index))

@admin.callback_query(F.data.startswith('sborka_gotov'))
async def process_sborka_gotov(callback: CallbackQuery):
    tg_id = int(callback.data.split('_')[-1])
    index = int(callback.data.split('_')[-2])
    if await readiness_sborka(index):
        await callback.message.delete()
        await callback.answer(f'Подтверждение сборки № {index} о готовности')
        await callback.bot.send_message(chat_id=tg_id, text=f'Ваш сборка № {index} приготовлена!', reply_markup=await admin_order())

@admin.callback_query(F.data == 'sborka_admin_nazad')
async def sborka_admin_nazad(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer('Заказы покупателей ->', reply_markup=await admin_order())

@admin.callback_query(F.data == 'admin_history')
async def process_admin_history(callback: CallbackQuery):
    await callback.message.edit_text('Подкатегории:', reply_markup=await admin_subcategories_stories())

@admin.callback_query(F.data == 'admin_history_catalog')
async def process_admin_history_catalog(callback: CallbackQuery):
    await callback.message.delete()
    history = await admin_history_get_inform_order()
    for item in history:
       position = '\n'.join([f'{k}: {v} шт.' for k, v in item[3].items()])
       await callback.message.answer(f'Заказ № {item[0]}\n\nДата готовности: {item[1]}\n\nАдрес доставки: {item[2]}\n\nПозиции: {position}\n\nПрайс: {item[4]}\n\nОПЛАТА: {"💳 Карта" if item[2] == "cart" else "💵 Наличка"}')
    await callback.message.answer('Вернуться к моим заказам!', reply_markup=admin_cancellation_history)
    
@admin.callback_query(F.data == 'admin_history_assembly')
async def process_history_assemby(callback: CallbackQuery):
    await callback.message.delete()
    history = await admin_history_get_inform_assembly()
    for sborka in history:
        if not sborka[2] == None:
            await callback.message.answer_photo(photo=sborka[2], caption=f"<b><i>Событие:</i></b> {sborka[1]}\n\n<b><i>Описание:</i></b> {sborka[3]}\n\n<b><i>Дата готовности:</i></b> {sborka[4]}")
        else:
            await callback.message.answer(f"<b><i>Событие:</i></b> {sborka[1]}\n\n<b><i>Описание:</i></b> {sborka[3]}\n\n<b><i>Дата готовности:</i></b> {sborka[4]}")
    await callback.message.answer('Вернуться к Моим заказам!', reply_markup=admin_cancellation_history)
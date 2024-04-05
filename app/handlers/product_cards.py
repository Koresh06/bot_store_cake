from aiogram import Router, F
from aiogram.types import CallbackQuery, FSInputFile
from aiogram.types.input_media_photo import InputMediaPhoto

from app.requests.product_cards_requests import (
    output_fast_food, 
    minus_count_product,
    plus_count_product,
    delete_cart,
    check_quantuty,
    add_cart_product,

)
from app.keyboards.inline_kb import (
    user_cart_product,
    add_cart,
    menu_catalog,
    user_categories,
)
from app.requests.admin_requests import output_categories
from app.keyboards.reply_rb import user_menu_kb


card = Router()

@card.callback_query(F.data.startswith('men.cat'))
@card.callback_query(F.data.startswith('user.categ'))
async def cmd_fast_food(callback: CallbackQuery):
    await callback.message.delete()
    try:
        if callback.data.split('_')[0] == 'men.cat':
            index = int(callback.data.split('_')[-1])
            categ = int(callback.data.split('_')[-2])
            item = await output_fast_food(categ)
            await callback.message.answer_photo(item[index][1], caption=f"🍰 <b><i>Наименование:</i></b> {item[index][0]}  \n\n🔖   <b><i>Состав/описание торта:</i></b> {item[index][2]}\n\n💵 <b><i>Прайс:</i></b> {item[index][3]} RUB за кг.", reply_markup=await    add_cart(int(callback.data.split('_')[1]), item[index][4], index))
            await callback.answer()
        elif callback.data.split('_')[0] == 'user.categ':
            item = await output_fast_food(int(callback.data.split('_')[-1]))
            await callback.message.answer_photo(item[0][1], caption=f"🍰 <b><i>Наименование:</i></b> {item[0][0]}  \n\n🔖   <b><i>Состав/описание торта:</i></b> {item[0][2]}\n\n💵 <b><i>Прайс:</i></b> {item[0][3]} RUB за кг.", reply_markup=await    add_cart(int(callback.data.split('_')[-1]), item[0][4]))
            await callback.answer()
    except IndexError:
        await callback.message.answer('На данный момент каталог продуктов пуст, загляните к нам чуть позже', reply_markup=await user_menu_kb())


@card.callback_query(F.data.startswith('forward'))
async def cmd_fast_food(callback: CallbackQuery):
    categ_id = int(callback.data.split('_')[-2])
    index = int(callback.data.split('_')[-1])
    item = await output_fast_food(categ_id)
    if item:
        if index < len(item) - 1:
            index += 1
            await callback.message.edit_media(media=InputMediaPhoto(media=item[index][1]))
            await callback.message.edit_caption(caption=f"🍰 <b><i>Наименование:</i></b> {item[index][0]}  \n\n🔖 <b><i>Состав/описание торта:</i></b> {item[index][2]}\n\n💵 <b><i>Прайс:</i></b> {item[index][3]} RUB за кг.", reply_markup=await add_cart(categ_id, item[index][4], index))
            await callback.answer()
        else:
            await callback.message.edit_media(media=InputMediaPhoto(media=item[0][1]))
            await callback.message.edit_caption(caption=f"🍰 <b><i>Наименование:</i></b> {item[0][0]}  \n\n🔖 <b><i>Состав/описание торта:</i></b>{item[0][2]}\n\n💵 <b><i>Прайс:</i></b> {item[0][3]} RUB за кг.", reply_markup=await add_cart(categ_id, item[0][4]))
            await callback.answer()
    else:
        await callback.message.answer('На данный момент каталог продуктов пуст, загляните к нам чуть позже')
        await callback.answer()

@card.callback_query(F.data.startswith('back'))
async def cmd_fast_food(callback: CallbackQuery):
    categ_id = int(callback.data.split('_')[-2])
    index = int(callback.data.split('_')[-1])
    item = await output_fast_food(categ_id)
    if item:
        if index > 0:
            index -= 1
            await callback.message.edit_media(media=InputMediaPhoto(media=item[index][1]))
            await callback.message.edit_caption(caption=f"🍰 <b><i>Наименование:</i></b>{item[index][0]}  \n\n🔖 <b><i>Состав/описание торта:</i></b> {item[index][2]}\n\n💵 <b><i>Прайс:</i></b>{item[index][3]} RUB за кг.", reply_markup=await add_cart(categ_id, item[index][4], index))
            await callback.answer()
        else:
            await callback.message.edit_media(media=InputMediaPhoto(media=item[-1][1]))
            await callback.message.edit_caption(caption=f"🍰 <b><i>Наименование:</i></b>{item[-1][0]}  \n\n<b><i>Состав/описание торта:</i></b> {item[-1][2]}   \n\n💵 <b><i>Прайс:</i></b>{item[-1][3]} RUB за кг.", reply_markup=await add_cart(categ_id, item[-1][4], len(item) - 1))
            await callback.answer()
    else:
        await callback.message.answer('На данный момент каталог продуктов пуст, загляните к нам чуть позже')
        await callback.answer()

@card.callback_query(F.data.startswith('count.value'))
async def count_quanty(callback: CallbackQuery):
    index = int(callback.data.split('_')[-2]) -1
    categ = int(callback.data.split('_')[-3])
    photo = FSInputFile("menu_tovar.jpg")
    await callback.message.edit_media(media=InputMediaPhoto(media=photo))
    await callback.message.edit_caption(caption='🗂|Товары', reply_markup=await menu_catalog(categ, index))
    await callback.answer()

#Уменьшении веса торт, при попытке менее 1, переход в исходную клавиатуру
@card.callback_query(F.data.endswith('minus'))
async def cmd_minus(callback: CallbackQuery):
    id_categ = int(callback.data.split('_')[0])
    id_product = int(callback.data.split('_')[1])
    index = int(callback.data.split('_')[2])
    if await minus_count_product(id_product):
        await callback.message.edit_reply_markup(reply_markup=await user_cart_product(id_categ, id_product, index))
    else:
        await delete_cart(callback.from_user.id, id_product)
        await callback.message.edit_reply_markup(reply_markup=await add_cart(id_categ, id_product, index))

#Вес торта, максимальный 5 кг.
@card.callback_query(F.data.endswith('plus'))
async def cmd_minus(callback: CallbackQuery):
    id_categ = int(callback.data.split('_')[0])
    id_product = int(callback.data.split('_')[1])
    index = int(callback.data.split('_')[2])
    if await plus_count_product(id_product):
        await callback.message.edit_reply_markup(reply_markup=await user_cart_product(id_categ, id_product, index))
    else:
        await callback.answer('Мы изготавливаем торты не более 5 кг.')

@card.callback_query(F.data.endswith('count'))
async def cmd_minus(callback: CallbackQuery):
    check_count = await check_quantuty(int(callback.data.split()[0]))
    await callback.answer(f'🎂 Торт {check_count} кг.')
    await callback.answer()


#При изменении количества изменяется клава
@card.callback_query(F.data.endswith('add_cart'))
async def cmd_add_cart(callback: CallbackQuery):
    id_categ = int(callback.data.split('_')[0])
    id_product = int(callback.data.split('_')[1])
    index = int(callback.data.split('_')[2])
    if await add_cart_product(callback.from_user.id, id_product):
        await callback.message.edit_reply_markup(reply_markup=await user_cart_product(id_categ, id_product, index))
        await callback.answer(text='Товар добавлен в корзину')
    else:
        await callback.answer('Товар уже был добавлен в корзину', show_alert=True)

@card.callback_query(F.data == 'bat_categ')
async def cmd_categ_back(callback: CallbackQuery):
    if await output_categories():
        await callback.message.delete()
        await callback.message.answer('Категории', reply_markup=await user_categories())
        await callback.answer()
    else:
        await callback.message.answer('Каталог пуст, для добавления нажмите ⬇️')
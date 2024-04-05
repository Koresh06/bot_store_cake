from aiogram import Router, F
from aiogram.types import Message

from app.requests.basket_user_requests import (
    check_user_cart,
    pars_product,
    delete_menu_product,
    clear_cart_pr,
)
from app.keyboards.reply_rb import (
    kb_menu_cart,
    user_menu_kb,

)


basket = Router()

@basket.message(F.text.endswith('Корзина'))
async def cmd_cart(message: Message):

    items = await check_user_cart(message.from_user.id)
    if items:
        lst_menu = []
        for item in items:
            parser_product_attr = await pars_product(item[0])
            lst_menu.append(parser_product_attr)

        content = '\n➖➖➖➖➖➖➖➖➖➖➖\n'.join([f"|-🍽 {lst_menu.index(item) + 1}. {item[0][0]}\n|-{item[1]} кг. х {item[0][1]} = {item [1] * item[0][1]} RUB" for item in lst_menu])
        total_cost = sum([i[1] * i[0][1] for i in lst_menu])
        name_count_product = [(item[0][0], item[1]) for item in lst_menu]

        await message.answer(text=f'🛒 Ваша корзина:\n\n{content}\n\n💸 ИТОГО: {total_cost} RUB', reply_markup=await kb_menu_cart(name_count_product))
        
    else:
        await message.answer('Корзина пуста, перейдите в котолог [📋 Меню] и сделайте свой выбор', reply_markup=await user_menu_kb())

#Удаление позиций из корзины
@basket.message(F.text.startswith('❌'))
async def cmd_delete_product(message: Message):
    name = message.text.split('.')[1]
    if await delete_menu_product(name):
        items = await check_user_cart(message.from_user.id)
        if items:
            lst_menu = []
            for item in items:
                parser_product_attr = await pars_product(item[0])
                lst_menu.append(parser_product_attr)

            content = '\n➖➖➖➖➖➖➖➖➖➖➖\n'.join([f"|-🍽 {lst_menu.index(item) + 1}. {item[0][0]}\n|-{item[1]} кг. х {item[0][1]} = {item[1] * item[0][1]} RUB" for item in lst_menu])
            total_cost = sum([i[1] * i[0][1] for i in lst_menu])
            name_count_product = [(item[0][0], item[1]) for item in lst_menu]

            await message.answer(text=f'🛒 Ваша корзина:\n\n{content}\n\n💸 ИТОГО: {total_cost} RUB', reply_markup=await  kb_menu_cart(name_count_product))
        else:
            await message.answer('Корзина пуста, перейдите в котолог [📋 Меню] и сделайте свой выбор', reply_markup=await user_menu_kb())

@basket.message(F.text.endswith('Очистить корзину'))
async def clear_cart(message: Message):
    if await clear_cart_pr(message.from_user.id):
        await message.answer('Корзина очищена, для пополнения переёдите в 📋 Меню)', reply_markup=await user_menu_kb())
    else:
        await message.answer('Ошибка, обратитесь к администратору [🤝 Помощь]')
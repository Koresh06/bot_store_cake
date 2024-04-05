from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import KeyboardButton


async def user_menu_kb():
    builder = ReplyKeyboardBuilder([
        [
            KeyboardButton(text='📋 Меню'),
            KeyboardButton(text='🛒 Корзина')    
        ],
        [
            KeyboardButton(text='📰 Мой Профиль'),
            KeyboardButton(text='📍 Мои заказы')
        ],
        [
            KeyboardButton(text='➡️ Другое'),
            KeyboardButton(text='🆘 Помощь')
        ]
    ])
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)

async def admin_menu_kb():
    builder = ReplyKeyboardBuilder([
        [
            KeyboardButton(text='✳️ Добавить товар'),
            KeyboardButton(text='👑 Пользователи'),
            KeyboardButton(text='📦 Заказы')
        ],
        [
            KeyboardButton(text='⬅️ Главное меню') 
        ]
    ])
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)

async def men_menu():
    builder = ReplyKeyboardBuilder([
        [
            KeyboardButton(text='🌐 Каталог'),
            KeyboardButton(text='🎂 Собрать свой торт')    
        ],
        [
            KeyboardButton(text='🛒 Корзина'),
        ],
        [
            KeyboardButton(text='⬅️ Главное меню'),
        ],
    ])
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)

async def kb_menu_cart(params):
    builder = ReplyKeyboardBuilder([
        [
            KeyboardButton(text='📋 Меню'),
            KeyboardButton(text='🚕 Оформить заказ'), 
        ]   
    ])

    for item in params:
        builder.row(KeyboardButton(text=f'❌ {params.index(item) + 1}. {item[0].strip()}. {item[1]} кг.'))
    builder.row(KeyboardButton(text='❎ Очистить корзину'))

    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)



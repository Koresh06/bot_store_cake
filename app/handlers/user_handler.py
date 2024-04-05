from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart, StateFilter, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state

from app.FSM.fsm import Telephone_user
from app.requests.user_requests import (
    chek_user,
    add_user, 
    show_phone,
)
from app.requests.admin_requests import output_categories
from app.keyboards.inline_kb import (
    new_user,
    user_categories,
    kb_help,
)
from app.keyboards.reply_rb import (
    user_menu_kb,
    men_menu,
)
import config


router = Router()

@router.message(F.text.endswith('Главное меню'))
@router.message(CommandStart(), StateFilter(default_state))
async def cmd_start(message: Message, state: FSMContext):
    user = await chek_user(message.from_user.id, message.from_user.first_name)
    if not user:
        await message.answer('Вас приветсвует кондитерская <b>ВКУСНЫЕ ТОРТЫ</b>')
        await message.answer('Укажите номер телефона в формате: +7ХХХхххХХХХ')
        await state.set_state(Telephone_user.phone)
    else:
        await message.answer('Доброго времени суток, мы рады вновь Вас приветствать в нашей кондитерской <b>ВКУСНЫЕ ТОРТЫ</b>\n\nДля работы с ботом выберите команду из меню ⬇️', reply_markup=await user_menu_kb())

@router.message(StateFilter(Telephone_user.phone))
async def cmd_telephone(message: Message, state: FSMContext):
    await state.update_data(phone=message.text)
    res = await state.get_data()
    if await add_user(message.from_user.id, message.from_user.first_name, res['phone']):
        await message.answer('✅ Регистрация успешно пройдена', reply_markup=await user_menu_kb())
        await message.bot.send_message(chat_id=config.ADMIN_ID, text=f'Новый пользователь - {message.from_user.first_name}', reply_markup=await new_user(message.from_user.id, message.from_user.first_name))
        await state.clear()
    else:
        await message.answer(f'Ошибка, обратитесь к администратору: {config.ADMIN_URL}')
        await state.clear()

@router.message(Command(commands='cancel'), StateFilter(default_state))
async def process_cancel_command(message: Message):
    await message.answer(
        text='Вы не заполняете форму, поэтому невозможно воспользоваться данной командой!'
    )

@router.message(Command(commands='cancel'), ~StateFilter(default_state))
async def process_cancel_command_state(message: Message, state: FSMContext):
    await message.answer(
        text='Отмена заполнения формы\n\nПри необходимости заполните форму заново'
    )
    await state.clear()

@router.message(F.text.endswith('Меню'))
async def cmd_categories_product(message: Message):
    await message.answer('Выберите из предложенного', reply_markup=await men_menu())

@router.message(F.text.endswith('Каталог'))
async def cmd_categories_product(message: Message):
    name_categories = await output_categories()
    if name_categories:
        await message.answer('Категории тортов', reply_markup=await user_categories())
    else:
        await message.answer('Каталог категорий пуст', reply_markup=await user_menu_kb())

@router.message(F.text.endswith('Мой Профиль'))
async def user_profile(message: Message):
    phone = await show_phone(message.from_user.id)
    await message.answer(f'┌📰 Ваш Профиль\n├Имя: <code>{message.from_user.first_name}</code>\n├ID: <code>{message.from_user.id}</code>\n├Телефон: <code>{phone}</code>\n└Количество заказов: <code>0 шт.</code>')

@router.message(F.text.endswith('Помощь'))
async def cmd_help(message: Message):
    await message.answer('🔸У вас возникли вопросы?\nМы с удовольствием ответим!\n', reply_markup=kb_help)

@router.message(F.text.endswith('Другое'))
async def cmd_drygoe(message: Message):
    await message.answer('Здесь будет информация о магазине/кондитерской', await user_menu_kb())
    

@router.message()
async def cmd_echo(message: Message):
    await message.answer('Данная команда/текст находится в разработке или вы пишите какую-то ерунду и бот Вас не понимает 🥴')
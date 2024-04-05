from aiogram.filters import BaseFilter
from aiogram.types import Message
import re


class CheckImageFilter(BaseFilter): 
    
    async def __call__(self, message: Message) -> bool:  
        if message.photo:
            return True
        else:
            await message.answer('Это не изображение, отправьте еще раз!')
            return False
        
class IsDigitFilter(BaseFilter):

    async def __call__(self, message: Message) -> bool:
        try:
            if message.text.isdigit() and isinstance(float(message.text), float):
                return True
        except ValueError:
            await message.answer('Не корректно указан прайс, попробуйте еще раз!')
            return False
        
class PhoneNumberVerification(BaseFilter):

    async def __call__(self, message: Message) -> bool:  
        if re.match(r'^(\+7|7|8)?[\s\-]?\(?[489][0-9]{2}\)?[\s\-]?[0-9]{3}[\s\-]?[0-9]{2}[\s\-]?[0-9]{2}$', message.text):
            return True
        else:
            await message.answer('Номер телефона введен не верно, попробуйте ещё раз!')
            return False
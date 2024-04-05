from app.database.models import async_session
from app.database.models import User, Cart, Orders
from sqlalchemy import select


async def chek_user(tg_id, username):
    async with async_session() as session:
        user_query = await session.scalar(select(User).where(User.tg_id == tg_id, User.username == username))
        if not user_query:
            return False
        
        return True
    
async def add_user(tg_id, username, phone):
    async with async_session() as session:
        try:
            session.add(User(tg_id=tg_id, username=username, phone=phone))
            session.add(Cart(user_id=tg_id))
            await session.commit()
            return True
        except Exception as exxit:
            print(exxit)
            return False
        
async def show_phone(tg_id):
    async with async_session() as session:
        phone = await session.scalar(select(User).where(User.tg_id == tg_id))
    return phone.phone

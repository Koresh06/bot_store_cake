from app.database.models import async_session
from app.database.models import User, Cart, Collecting_the_cake
from sqlalchemy import select


#Добавление в БД сборки торта
async def collecting_cake(res, tg_id):
    async with async_session() as session:
        try:
            user_d = await session.scalar(select(User).where(User.tg_id == tg_id))
            cart_d = await session.scalar(select(Cart).where(Cart.user_id == tg_id))
            session.add(Collecting_the_cake(user_id=user_d.id, cart_id=cart_d.id, event=res['event'], image=res['image'], description=res['description'], data=res['data']))
            await session.commit()
            return True
        except Exception as exxit:
            print(exxit)
            return False
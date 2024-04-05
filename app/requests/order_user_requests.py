from app.database.models import async_session
from app.database.models import User, Orders, Collecting_the_cake
from sqlalchemy import select


async def nomer_order(tg_id):
    async with async_session() as session:
        user_d = await session.scalar(select(User).where(User.tg_id == tg_id))
        nomer_d = await session.execute(select(Orders.id).where(Orders.user_id == user_d.id))
    return nomer_d.all()

async def nomer_assembly_user(tg_id):
    async with async_session() as session:
        user_d = await session.scalar(select(User).where(User.tg_id == tg_id))
        nomer_d = await session.execute(select(Collecting_the_cake.id).where(Collecting_the_cake.user_id == user_d.id))
    return nomer_d.all()

async def get_inform_assembly(index):
    async with async_session() as session:
        orders_d = await session.execute(select(Collecting_the_cake.id, Collecting_the_cake.event, Collecting_the_cake.image, Collecting_the_cake.description, Collecting_the_cake.data).where(Collecting_the_cake.id == index))
    return orders_d.all()

async def delete_sborka(id):
    async with async_session() as session:
        try:
            order = await session.scalar(select(Collecting_the_cake).where(Collecting_the_cake.id == id))
            await session.delete(order)
            await session.commit()
            return True
        except Exception() as ex:
            print(ex)
            return False

async def get_inform_order(index):
    async with async_session() as session:
        orders_d = await session.execute(select(Orders.id, Orders.data_time, Orders.method, Orders.order, Orders.total_cost, Orders.status, Orders.readiness).where(Orders.id == index))
    return orders_d.all()

async def history_get_inform_order(tg_id):
    async with async_session() as session:
        user_d = await session.scalar(select(User).where(User.tg_id == tg_id))
        orders_d = await session.execute(select(Orders.id, Orders.data_time, Orders.method, Orders.order, Orders.total_cost, Orders.status, Orders.readiness).where(Orders.user_id == user_d.id, Orders.readiness == True))
    return orders_d.all()

async def history_get_inform_assembly(tg_id):
    async with async_session() as session:
        user_d = await session.scalar(select(User).where(User.tg_id == tg_id))
        orders_d = await session.execute(select(Collecting_the_cake.id, Collecting_the_cake.event, Collecting_the_cake.image,   Collecting_the_cake.description, Collecting_the_cake.data).where(Collecting_the_cake.user_id == user_d.id, Collecting_the_cake.readiness == True))
        return orders_d.all()
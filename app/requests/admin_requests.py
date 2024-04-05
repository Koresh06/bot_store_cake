from app.database.models import async_session
from app.database.models import User, Product, Categories, Orders, Collecting_the_cake
from sqlalchemy import select, update


async def output_categories():
    async with async_session() as session:
        name_cat = await session.execute(select(Categories.name, Categories.id))
    return name_cat.all()

async def add_categories(name_cat):
    async with async_session() as session:
        name_d = await session.scalar(select(Categories).where(Categories.name == name_cat))
        if not name_d:
            session.add(Categories(name=name_cat))
            await session.commit()
            return True
        else:
            return False
        
async def add_product_db(tg_id, product: dict):
    async with async_session() as session:
        try:
            user_d = await session.scalar(select(User).where(User.tg_id == tg_id))
            session.add(Product(user_id=user_d.id, categories_id=product['id_categ'], name=product['name'],   image=product['image'], description=product   ['description'], price=product['price']))
            count = await session.scalar(select(Categories.count).where(Categories.id == product['id_categ']))
            count += 1
            await session.execute(update(Categories).where(Categories.id == product['id_categ']).values(count=count))
            await session.commit()
            return True
        except Exception as exxit:
            print(exxit)
            return False
        finally:
            session.commit()
    
#Откланение заказа   
async def delete_orders(id):
    async with async_session() as session:
        try:
            order = await session.scalar(select(Orders).where(Orders.id == id))
            await session.delete(order)
            await session.commit()
            return True
        except Exception() as ex:
            print(ex)
            return False
        
#Получение списка пользователей
async def users():
    async with async_session() as session:
        users_d = await session.execute(select(User.username, User.tg_id))
        if users_d:
            return users_d.all()
        return False
    
#Номера заказов находящихся в работе   
async def admin_nomer_zak():
    async with async_session() as session:
        nomer_d = await session.execute(select(Orders.id, Orders.user_id).where(Orders.readiness == False))
    return nomer_d

async def get_tg_id(user_id):
    async with async_session() as session:
        print(user_id)
        user_d = await session.scalar(select(User).where(User.id == user_id))
    return user_d.tg_id

async def get_info_admin_order(index):
    async with async_session() as session:
        orders_d = await session.execute(select(Orders.id, Orders.data_time, Orders.method, Orders.order, Orders.total_cost, Orders.status).where(Orders.readiness == False, Orders.id == index))
    return orders_d.all()

#Подтверждение готовности заказа
async def readiness_order(index):
    async with async_session() as session:
        if await session.execute(update(Orders).where(Orders.id == index).values(readiness=True)):
            await session.commit()
            return True
        return False
    
async def get_sborka_nomer_admin():
    async with async_session() as session:
        nomer_d = await session.execute(select(Collecting_the_cake.id, Collecting_the_cake.user_id).where(Collecting_the_cake.readiness == False))
    return nomer_d

async def get_inform_assembly_admin(index):
    async with async_session() as session:
        orders_d = await session.execute(select(Collecting_the_cake.id, Collecting_the_cake.event, Collecting_the_cake.image, Collecting_the_cake.description, Collecting_the_cake.data).where(Collecting_the_cake.readiness == False, Collecting_the_cake.id == index))
    return orders_d.all()

async def readiness_sborka(index):
    async with async_session() as session:
        if await session.execute(update(Collecting_the_cake).where(Collecting_the_cake.id == index).values(readiness=True)):
            await session.commit()
            return True
        return False
    
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
        
async def admin_history_get_inform_order():
    async with async_session() as session:
        orders_d = await session.execute(select(Orders.id, Orders.data_time, Orders.method, Orders.order, Orders.total_cost, Orders.status, Orders.readiness).where(Collecting_the_cake.readiness == True))
    return orders_d.all()

async def admin_history_get_inform_assembly():
    async with async_session() as session:
        orders_d = await session.execute(select(Collecting_the_cake.id, Collecting_the_cake.event, Collecting_the_cake.image,   Collecting_the_cake.description, Collecting_the_cake.data).where(Collecting_the_cake.readiness == True))
        return orders_d.all()
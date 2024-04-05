from app.database.models import async_session
from app.database.models import User, Cart, CartItem, Product, Orders
from sqlalchemy import select, update


#Сбор id_product и количества товара для оплаты
async def payment_cart(tg_id):
    async with async_session() as session:
        cart_d = await session.scalar(select(Cart).where(Cart.user_id == tg_id))
        cartitem_d = await session.execute(select(CartItem.product_id, CartItem.quantuty).where(CartItem.cart_id == cart_d.id))
    return cartitem_d.all()

#Название, описание и прайс
async def product_name_desc_price(id_pord):
    async with async_session() as session:
        product_d = await session.execute(select(Product.name, Product.price).where(Product.id == id_pord))
    return product_d.all()

async def adding_order_information(tg_id, cake, method, data, price):
    async with async_session() as session:
        try:
            user_d = await session.scalar(select(User).where(User.tg_id == tg_id))
            cart_d = await session.scalar(select(Cart).where(Cart.user_id == tg_id))
            session.add(Orders(user_id=user_d.id, cart_id=cart_d.id, method=method, data_time=data, order=cake, total_cost=float  (price)))
            await session.commit()
            return True
        except Exception as exxit:
            return False
        finally: 
            await session.commit()

#Последний заказ пользователя
async def id_order_user(tg_id):
    async with async_session() as session:
        user_d = await session.scalar(select(User).where(User.tg_id == tg_id))
        orders_d = await session.execute(select(Orders.id).where(Orders.user_id == user_d.id))
    return orders_d

#Получаем данные для уведомления админа об оформлении заказа
async def retrieve_data(index):
    async with async_session() as session:
        order = await session.execute(select(Orders.id, Orders.data_time, Orders.order, Orders.total_cost, Orders.method).where(Orders.id == index))
    return order.all()

async def payment_confirmation(id_):
    async with async_session() as session:
        await session.execute(update(Orders).where(Orders.id == id_).values(status=1))
        await session.commit()

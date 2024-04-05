from app.database.models import async_session
from app.database.models import Cart, CartItem, Product
from sqlalchemy import select


async def check_user_cart(tg_id):
    async with async_session() as session:
        user_d = await session.scalar(select(Cart).where(Cart.user_id == tg_id))
        product_d = await session.execute(select(CartItem.product_id).where(Cart.id == user_d.id))
        if product_d:
            return product_d.all()
        return False
    
async def pars_product(id_pr):
    async with async_session() as session:
        attr_pr = await session.execute(select(Product.name, Product.price).where(Product.id == id_pr))
        count = await session.scalar(select(CartItem.quantuty).where(CartItem.product_id == id_pr))
        return *attr_pr.all(), count
    
async def delete_menu_product(name):
    async with async_session() as session:
        try:
            name_d = await session.scalar(select(Product).where(Product.name == name.strip()))
            del_pr = await session.scalar(select(CartItem).where(CartItem.product_id == name_d.id))
            await session.delete(del_pr)
            await session.commit()
            return True
        except Exception as ex:
            print(ex)
            return False
        
#Очистка корзины (полностью)
async def clear_cart_pr(tg_id):
    async with async_session() as session:
        try:
            user_d = await session.scalar(select(Cart).where(Cart.user_id == tg_id))
            clear_d = await session.scalars(select(CartItem).where(CartItem.cart_id == user_d.id))
            for clear in clear_d:
                await session.delete(clear)
            await session.commit()
            return True
        except Exception as ex:
            print(ex)
            return False
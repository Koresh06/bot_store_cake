from app.database.models import async_session
from app.database.models import Cart, CartItem, Product
from sqlalchemy import select, update


async def output_fast_food(id_categ) -> list:
    async with async_session() as session:
        fast_food = await session.execute(select(Product.name, Product.image, Product.description, Product.price, Product.id).where(Product.categories_id == id_categ))
        if fast_food:
            return fast_food.all()
        return False     
    
async def minus_count_product(id_product):
    async with async_session() as session:
        count = await session.scalar(select(CartItem.quantuty).where(CartItem.product_id == id_product))
        if count > 1:
            count -= 1
            await session.execute(update(CartItem).where(CartItem.product_id == id_product).values(quantuty=count))
            await session.commit()
            return True
        return False
    
async def plus_count_product(id_product):
    async with async_session() as session:
        count = await session.scalar(select(CartItem.quantuty).where(CartItem.product_id == id_product))
        if count < 5:
            count += 1
            await session.execute(update(CartItem).where(CartItem.product_id == id_product).values(quantuty=count))
            await session.commit()
            return True
        return False
    
async def delete_cart(tg_id, data):
    async with async_session() as session:
        try:
            user_d = await session.scalar(select(Cart).where(Cart.user_id == tg_id))
            product_item = await session.scalar(select(Product).where(Product.id == data))
            del_item_cart = await session.scalar(select(CartItem).where(CartItem.cart_id == user_d.id, CartItem.product_id == product_item.id))
            await session.delete(del_item_cart)
            await session.commit()
            return True
        except Exception as exxit: 
            print(exxit)
            return False
        
async def check_quantuty(id_product):
    async with async_session() as session:
        quantuty = await session.scalar(select(CartItem.quantuty).where(CartItem.product_id == id_product))
    return quantuty

async def add_cart_product(tg_id, id_categ):
    async with async_session() as session:
        cart_user = await session.scalar(select(Cart).where(Cart.user_id == tg_id))
        product_item = await session.scalar(select(Product).where(Product.id == int(id_categ)))
        check_cartitem = await session.scalar(select(CartItem).where(CartItem.cart_id == cart_user.id, CartItem.product_id == product_item.id))
        if not check_cartitem:
            session.add(CartItem(cart_id=cart_user.id, product_id=product_item.id))
            await session.commit()
            return True
        else: 
            return False
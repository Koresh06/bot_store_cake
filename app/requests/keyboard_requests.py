from app.database.models import async_session
from app.database.models import Product, Categories
from sqlalchemy import select

async def count_quantuty(categ_id):
    async with async_session() as session:
        count = await session.scalar(select(Categories.count).where(Categories.id == categ_id))
        print(count)
    return count

#Меню категорий, вывод имен тортов
async def check_name_cake(categ):
    async with async_session() as session:
        cake_lst = await session.execute(select(Product.name).where(Product.categories_id == categ))
    return cake_lst.all()

import io
import os
import requests
from dotenv import load_dotenv, find_dotenv
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from PIL import Image

load_dotenv(find_dotenv())

async def create_order_pdf(username, order):
    font_path = "Arial.ttf"  # Путь к шрифту
    buffer = io.BytesIO()
    pdfmetrics.registerFont(TTFont("Arial", font_path))

    c = canvas.Canvas(buffer, pagesize=letter)
    c.setFont("Arial", 12)

    c.drawString(100, 750, "Детали заказа:")
    y = 730
    item = order[0]
    y -= 20
    text_lines = [
        f"Заказчик: {username}",
        f"Заказ: №{item[0]}",
        f"Дата готовности: {item[1]}",
        f"Позиции: {item[2]}",
        f"Прайс: {item[3]}",
        f'ОПЛАТА: {"Карта" if item[4] == "cart" else "Наличка"}'
    ]
    for line in text_lines:
        c.drawString(100, y, line)
        y -= 20  # уменьшаем координату y для следующей строки
    c.save()
    buffer.seek(0)  # Устанавливаем позицию чтения в начало буфера
    return buffer.read()  # Возвращаем данные из буфера


async def create_assembly_pdf(username, order):
    # Загрузка изображения из URL, если оно есть
    if order['image']:
        token = os.getenv('TOKEN')
        file_info_url = f"https://api.telegram.org/bot{token}/getFile"
        file_info_response = requests.get(file_info_url, params={"file_id": order['image']})
        file_info_data = file_info_response.json()
        file_path = file_info_data["result"]["file_path"]
        
        download_url = f"https://api.telegram.org/file/bot{token}/{file_path}"
        image_response = requests.get(download_url)
        
        # Создание объекта изображения
        image_data = io.BytesIO(image_response.content)
        try:
            image = Image.open(image_data)
        except Exception as e:
            raise ValueError(f"Failed to open image: {str(e)}")
    
    # Создание PDF
    font_path = "Arial.ttf"  # Путь к шрифту
    buffer = io.BytesIO()
    pdfmetrics.registerFont(TTFont("Arial", font_path))
    c = canvas.Canvas(buffer, pagesize=letter)
    c.setFont("Arial", 12)
    c.drawString(100, 750, "Детали заказа:")
    y = 730
    y -= 20
    
    # Добавление информации о заказе
    text_lines = [
        f"Заказчик: {username}",
        f"Событие: {order['event']}",
        f"Описание: {order['description']}",
        f"Дата готовности: {order['data']}",
    ]
    for line in text_lines:
        c.drawString(100, y, line)
        y -= 20  # уменьшаем координату y для следующей строки
    
    # Если есть изображение, сохраняем его в файл и добавляем в PDF
    if order['image']:
        # Сохранение изображения в файл
        image_path = "temp_image.jpg"
        image.save(image_path)
        
        # Добавление изображения в PDF с отступами
        image_width, image_height = image.size
        aspect_ratio = image_width / image_height
        target_height = 200  # Установите высоту изображения по вашему усмотрению
        target_width = int(target_height * aspect_ratio)
        x_offset = (letter[0] - target_width) / 2  # центрирование изображения по горизонтали
        c.drawImage(image_path, x_offset, y - target_height - 20, width=target_width, height=target_height)
        
        # Удаление временного файла изображения
        os.remove(image_path)
    
    c.save()
    buffer.seek(0)
    
    return buffer.getvalue()
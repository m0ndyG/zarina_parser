import scrapy

class ZarinaProduct(scrapy.Item):
    url = scrapy.Field()                     # Ссылка на товар
    category = scrapy.Field()                # Категория/Подкатегории (например, "Женщинам > Платья")
    name = scrapy.Field()                    # Название товара
    product_code = scrapy.Field()            # Код товара (артикул)
    price_regular = scrapy.Field()           # Цена без скидки
    price_discounted = scrapy.Field()        # Цена со скидкой (если есть)
    characteristics = scrapy.Field()         # Все характеристики (словарь или список словарей)
    availability = scrapy.Field()            # Наличие (например, число или строка "В наличии"/"Нет в наличии")
    image_urls = scrapy.Field()              # Список ссылок на фото
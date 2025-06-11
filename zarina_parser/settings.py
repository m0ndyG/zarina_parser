import os
from datetime import datetime

BOT_NAME = "zarina_parser"
SPIDER_MODULES = ["zarina_parser.spiders"]
NEWSPIDER_MODULE = "zarina_parser.spiders"

# Следовать правилам robots.txt
ROBOTSTXT_OBEY = False

# Задержка между запросами
DOWNLOAD_DELAY = 1

# Кастомный User-Agent
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'

# Настройки логирования
LOG_LEVEL = "INFO"
os.makedirs("logs", exist_ok=True)
LOG_FILE = f"./logs/{datetime.now().strftime('%Y.%m.%d')}.log"

# Настройки экспорта данных
FEEDS = {
    'products.json': {
        'format': 'json',
        'encoding': 'utf-8',
        'store_empty': False,
        'overwrite': True,
        'indent': 4, # Для красивого форматирования JSON
        'fields': [
            'url', 'category', 'name', 'product_code',
            'price_regular', 'price_discounted', 'characteristics',
            'availability', 'image_urls'
        ]
    }
}
FEED_EXPORT_ENCODING = "utf-8"
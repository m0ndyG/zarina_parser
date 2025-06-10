import scrapy
import json
import re
import codecs
from urllib.parse import urlparse, parse_qs, urlencode

from ..items import ZarinaProduct

class ZarinaSpider(scrapy.Spider):
    name = 'zarina'
    
    CATEGORY_URLS = {
        'women': 'https://zarina.ru/catalog/clothes/',
        'men': 'https://zarina.ru/man/clothes/',
    }

    def start_requests(self):
        category_to_parse = getattr(self, 'category', 'all')
        if category_to_parse == 'all':
            self.logger.info("Режим 'all': парсим все категории.")
            for url in self.CATEGORY_URLS.values():
                yield scrapy.Request(url, self.parse)
        elif category_to_parse in self.CATEGORY_URLS:
            self.logger.info(f"Режим '{category_to_parse}': парсим только одну категорию.")
            yield scrapy.Request(self.CATEGORY_URLS[category_to_parse], self.parse)
        else:
            self.logger.error(f"Неизвестная категория: '{category_to_parse}'. Доступные: 'women', 'men', 'all'.")

    def parse(self, response):
        self.logger.info(f"Парсинг страницы каталога: {response.url}")


        if '/man/' in response.url:
            main_category = 'Мужчинам'
        else:
            main_category = 'Женщинам'

        script_text = response.xpath("//script[contains(., 'self.__next_f.push') and contains(., 'products')]/text()").get()
        if not script_text:
            self.logger.error(f"Не удалось найти скрипт с данными на странице {response.url}")
            return
            
        match = re.search(r'self\.__next_f\.push\(\[1,"[^:]*:(.*)"\]\)', script_text, re.DOTALL)
        if not match:
            self.logger.error(f"Не удалось извлечь JSON-строку из скрипта на {response.url}")
            return
            
        js_string_literal = match.group(1)
        
        try:
            json_string = codecs.decode(js_string_literal, 'unicode_escape')
            data = json.loads(json_string)
        except (json.JSONDecodeError, TypeError) as e:
            self.logger.error(f"Ошибка декодирования JSON на {response.url}: {e}", exc_info=True)
            return

        def find_block(d, key_to_find):
            if isinstance(d, dict) and key_to_find in d: return d
            if isinstance(d, dict):
                for value in d.values():
                    if (found := find_block(value, key_to_find)): return found
            elif isinstance(d, list):
                for item in d:
                    if (found := find_block(item, key_to_find)): return found
            return None

        data_block = find_block(data, 'products') or {}
        products = data_block.get('products', [])
        pagination = data_block.get('pagination', {})

        for product_info in products:
            item = ZarinaProduct()
            product_id = product_info.get('id')
            if not product_id:
                self.logger.warning(f"Не найден ID для товара, пропускаем. Инфо: {product_info}")
                continue
            
            item['url'] = response.urljoin(f"/catalog/product/{product_id}/")
            
            yield scrapy.Request(
                url=item['url'],
                callback=self.parse_product_page,
                meta={'item': item, 'product_info': product_info, 'main_category': main_category}
            )

        current_page = pagination.get('current_page', 1)
        total_pages = pagination.get('total_pages', 1)

        if current_page < total_pages:
            next_page_num = current_page + 1
            parsed_url = urlparse(response.url)
            query_params = parse_qs(parsed_url.query)
            query_params['PAGEN_1'] = [str(next_page_num)]
            next_page_url = parsed_url._replace(query=urlencode(query_params, doseq=True)).geturl()
            
            self.logger.info(f"Переход на следующую страницу каталога: {next_page_url}")
            yield response.follow(next_page_url, callback=self.parse)

    def parse_product_page(self, response):
        self.logger.info(f"Парсинг страницы товара: {response.url}")
        item = response.meta['item']
        product_info = response.meta['product_info']
        main_category = response.meta['main_category']
        item['category'] = f"Главная > {main_category} > Одежда"
            
        raw_name = product_info.get('name', '')
        try: item['name'] = raw_name.encode('latin-1').decode('utf-8')
        except: item['name'] = raw_name
            
        item['product_code'] = product_info.get('id')
        price = product_info.get('price', {})
        item['price_regular'] = price.get('common_price')
        item['price_discounted'] = price.get('discount_price')
            
        item['availability'] = sum(o.get('online_quantity', 0) + o.get('retail_quantity', 0) for o in product_info.get('offers', []))
        item['image_urls'] = json.dumps([response.urljoin(m.get('original_url')) for m in product_info.get('media', [])], ensure_ascii=False)

        characteristics = {}
        char_divs = response.xpath("//div[div/text()='О товаре']/following-sibling::div[1]/div")
        
        for div in char_divs:
            key_raw = div.xpath('./span/text()').get()
            if not key_raw: continue
            
            key = key_raw.replace(':', '').strip()
            value = " ".join(div.xpath('./text()').getall()).strip()
            
            if key and value:
                characteristics[key] = value
        
        item['characteristics'] = json.dumps(characteristics, ensure_ascii=False)
        yield item
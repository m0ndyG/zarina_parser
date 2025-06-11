import json
import pandas as pd
import os

def convert_json_to_xlsx(json_path='products.json', xlsx_path='products.xlsx'):
    """
    Конвертирует JSON-файл со списком товаров в XLSX-файл.
    """
    if not os.path.exists(json_path):
        print(f"Ошибка: JSON-файл не найден по пути '{json_path}'")
        return

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if not data:
        print("JSON-файл пуст. Нет данных для конвертации.")
        return

    df = pd.DataFrame(data)

    # Задаем нужный порядок колонок
    columns_order = [
        'url', 'category', 'name', 'product_code',
        'price_regular', 'price_discounted', 'characteristics',
        'availability', 'image_urls'
    ]
    df = df[columns_order]

    df.to_excel(xlsx_path, index=False, engine='openpyxl')
    print(f"Конвертация успешно завершена. Данные сохранены в '{xlsx_path}'")

if __name__ == '__main__':
    convert_json_to_xlsx()
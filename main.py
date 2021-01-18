import requests
import sqlite3
import threading
from pathlib import Path 
from bs4 import BeautifulSoup
import base64
import json
#src
from src.data_handler import DBHandler
import src.shop_handler as shop_handler
from src.global_settings import GlobalSettings

def main():
    GlobalSettings()
    data_handler = DBHandler('data.db')
    data_handler.connect()
    data = data_handler.get_main_list()
    senseis_products = get_senseis_products(data)
    date, lastest_senseis_products, lastest_shop_products, all_products =\
        data_handler.get_product_update(senseis_products)
    if len(lastest_senseis_products) > 0:
        checked = input('New products, check?:')
        if checked.lower().startswith('y'): 
            data_handler.write_product_update(lastest_shop_products, all_products)
    else:
        print("No change since %s"%date)    
    file = open('testout.json', 'w', encoding='utf-8')
    file.write(json.dumps(lastest_senseis_products, sort_keys=True, indent=2, ensure_ascii = False))
    file.close()
    
def get_senseis_products(data):
    senseis_products = {}
    for sensei_name, shops in data.items():
        senseis_products[sensei_name] = []
        for shop_name, shop_url in shops.items():
            product_infos = shop_handler.get_product_infos(shop_name, shop_url, sensei_name)
            for info in product_infos:
                info_dict = info.get_dict_info()
                if GlobalSettings.download_thumb:
                    info_dict['thumb_bytes'] = base64.b64encode(info_dict['thumb_bytes']).decode('ascii')
                senseis_products[sensei_name] += (info_dict,)
                
    return senseis_products

main()
        
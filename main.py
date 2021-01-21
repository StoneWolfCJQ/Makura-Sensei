import requests
import sqlite3
import threading
from pathlib import Path 
from bs4 import BeautifulSoup
import base64
import json
from datetime import datetime
#src
from src.data_handler import DBHandler
import src.shop_handler as shop_handler
from src.global_settings import GlobalSettings
import src.file_handler as file_handler

def main():
    GlobalSettings()
    data_handler = DBHandler('data.db')
    data_handler.connect()
    data = data_handler.get_main_list()
    senseis_products = get_senseis_products(data)
    date, lastest_senseis_products, lastest_shop_products, all_products =\
        data_handler.get_product_update(senseis_products)
    current_date_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if len(lastest_senseis_products) > 0:
        download = input('New products, download thumb?: ')
        if download.lower().startswith('y'):
            print("downloading...")
            shop_handler.fill_product_thumbs(lastest_senseis_products)
            print("writing...")
            file_handler.create_thumb_file(lastest_senseis_products, \
                "New/%s/"%current_date_time.split()[0])
        checked = input('Check new?: ')
        if checked.lower().startswith('y'): 
            data_handler.write_product_update(current_date_time, lastest_shop_products, all_products)
        else:
            print("New products unchecked")
    else:
        print("No change since %s"%date)
    file = open('testout.json', 'w', encoding='utf-8')
    file.write(json.dumps(lastest_senseis_products, sort_keys=True, indent=2, ensure_ascii = False, cls = file_handler.ProductEncoder))
    file.close()
    input("Press any key")
    
def get_senseis_products(data):
    senseis_products = {}
    for sensei_name, shops in data.items():
        senseis_products[sensei_name] = []
        for shop_name, shop_url in shops.items():
            product_infos = shop_handler.get_product_infos(shop_name, shop_url, sensei_name)         
            senseis_products[sensei_name] += product_infos   
    return senseis_products

main()
        
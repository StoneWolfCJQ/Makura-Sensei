import sqlite3
import json
import copy
from datetime import datetime
from .product_info import *
class DBHandler():
    def __init__(self, db_path):
        self.db_path = db_path
        self.cursor = None
        
    def connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        self.cursor = conn.cursor()

    '''
    output format: {
        'TwinBox': {
            'Booth': 'http...',
            ...
        },
        ...
    }
    '''
    def get_main_list(self):
        data = self.cursor.execute('SELECT * FROM MainList')
        output = {}
        for row in data:
            if not row['_Watch']: continue
            sensei_name = row['_Name'] 
            output[sensei_name] = {}  
            for col in row.keys():
                if col.startswith('_'): continue
                shop_name = col    
                shop_address = row[shop_name]
                if self.is_shop_address(shop_address):
                    output[sensei_name][shop_name] = shop_address
        return output

    '''
    json string: {
        'Booth': [
            '1254125', ...
        ],
        ...
    }
    the last one is new latest one
    '''
    def get_last_shops_products(self):
        data = self.cursor.execute('SELECT date, all_products FROM LastCheck ORDER BY id DESC LIMIT 1')
        row = data.fetchone()
        if row == None:
            return '', {}
        else:
            return row['date'], json.loads(row['all_products'])
        
        
    def get_product_update(self, senseis_products):
        date, last_shops_products = self.get_last_shops_products()
        latest_shops_products = {}
        latest_senseis_products = copy.deepcopy(senseis_products)
        all_products = {}
        for sensei_name, products in senseis_products.items():
            for product in products:
                info = type('ProductInfo', (object,), product)
                if info.stocks != "No":
                    if not info.shop_name in latest_shops_products:
                        latest_shops_products[info.shop_name] = []
                        all_products[info.shop_name] = []
                    if not info.shop_name in last_shops_products or\
                        not info.product_id in last_shops_products[info.shop_name]:
                        latest_shops_products[info.shop_name].append(info.product_id)
                    else:
                        latest_senseis_products[sensei_name].remove(product)
                    all_products[info.shop_name].append(info.product_id)
                else:
                    latest_senseis_products[sensei_name].remove(product)
                if len(latest_senseis_products[sensei_name]) <= 0:
                    latest_senseis_products.pop(sensei_name)
        return  date, latest_senseis_products, latest_shops_products, all_products
    
    def write_product_update(self, latest_shops_products, all_products):
        products_json = json.dumps(latest_shops_products)
        aproducts_json = json.dumps(all_products)
        date_string = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        command = "INSERT INTO LastCheck(date, new_products, all_products) VALUES('%s', '%s', '%s')"\
            %(date_string, products_json, aproducts_json)
        self.cursor.execute(command)
        self.cursor.connection.commit()
                
    def is_shop_address(self, cell_value):
        return cell_value.startswith('http')
    
        
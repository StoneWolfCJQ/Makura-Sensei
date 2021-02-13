import sqlite3
import json
import copy
import re
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
        data = self.cursor.execute('SELECT * FROM MainList WHERE _Watch = 1')
        output = {}
        for row in data:
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
    {
        'TwinBox': ['Keyword', ...],
        ...
    }
    '''
    def get_product_filter(self):
        data = self.cursor.execute('SELECT _Name, _Keyword FROM MainList WHERE _Watch = 1')
        output = {}
        for row in data:
            output[row['_Name']] = self.format_keyword(row['_Keyword'])
        return output

    def get_product_filter2(self, sensei_name):
        data = self.cursor.execute('SELECT _Keyword FROM MainList WHERE _Name = "%s"'%sensei_name)
        row = data.fetchone()
        if row == None:
            raise Exception("No such sensei %s"%sensei_name)
        else:
            a = self.format_keyword(row[0])
            return a

    def format_keyword(self, keywords):
        kk = keywords.split()
        nk = []
        for k in kk:
            if (k.strip()):
                nk.append(k.strip()) 
        if len(nk) == 0:
            nk.append('.*')
        return nk

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
        latest_senseis_products = {}
        all_products = {}
        for sensei_name, products in senseis_products.items():
            for product in products:
                if product.stocks != "No" and \
                    any(re.search(word, product.product_name) for word in self.get_product_filter2(sensei_name)):
                    if not product.shop_name in latest_shops_products:
                        latest_shops_products[product.shop_name] = []
                        all_products[product.shop_name] = []
                    if not product.shop_name in last_shops_products or\
                        not product.product_id in last_shops_products[product.shop_name]:
                        if not sensei_name in latest_senseis_products:
                            latest_senseis_products[sensei_name] = []
                        latest_senseis_products[sensei_name].append(product)
                        latest_shops_products[product.shop_name].append(product.product_id)
                    all_products[product.shop_name].append(product.product_id)
        return  date, latest_senseis_products, latest_shops_products, all_products
    
    def write_product_update(self, date_time, latest_shops_products, all_products):
        products_json = json.dumps(latest_shops_products)
        aproducts_json = json.dumps(all_products)
        command = "INSERT INTO LastCheck(date, new_products, all_products) VALUES('%s', '%s', '%s')"\
            %(date_time, products_json, aproducts_json)
        self.cursor.execute(command)
        self.cursor.connection.commit()
                
    def is_shop_address(self, cell_value):
        return cell_value.startswith('http')
    
        
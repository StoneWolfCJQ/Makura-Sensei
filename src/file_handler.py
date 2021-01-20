from pathlib import Path
from sys import getsizeof
import json
def create_thumb_file(sensei_products, path):
    Path(path).mkdir(exist_ok = True)
    for sensei_name, products in sensei_products.items():
        for product in products:
            content = product.thumb_bytes
            file_path = path + "-".join([product.sensei_name, product.shop_name, product.product_id,\
                product.product_name, product.price]) + ".png"            
            p = Path(file_path)
            #if not p.exists() or p.stat().st_size != getsizeof(content) - getsizeof(bytes()):
            file = open(file_path, 'wb')
            file.write(content)
            file.close()

class ProductEncoder(json.JSONEncoder):
    def default(self, o):
        o.thumb_bytes = ''
        return o.__dict__
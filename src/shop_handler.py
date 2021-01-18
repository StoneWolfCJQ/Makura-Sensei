from bs4 import BeautifulSoup
import requests
import abc
import time
import re
from .global_settings import GlobalSettings     
from .product_info import * 

class BaseHandler():
    fetching_count = 0
    fetching_limit = 5
    
    def __init__(self):    
        self.cookies = {}
        self.need_proxie = True        
        
    def get_product_infos(self, shop_url): 
        if self.need_proxie:
            r = requests.get(shop_url, 
                         proxies = GlobalSettings.proxies, 
                         cookies = self.cookies)
        else:
            r = requests.get(shop_url, 
                         cookies = self.cookies)
            
        html = r.text
        soup = BeautifulSoup(html, 'lxml')
        item_list = self.get_item_list_from_soup(soup)
        product_infos = []
        for item in item_list:
            info = ProductInfo("", "", 
                               self.get_product_name(item),
                               self.get_product_id(item),
                               self.get_price(item),
                               self.get_stocks(item),
                               self.get_thumb_url(item),
                               self.get_thumb_bytes(item)
                               )
            product_infos.append(info)
        return product_infos
        
        
    def get_item_list_from_soup(self, soup):
        raise NotImplementedError
    
    def get_product_id(self, item):
        raise NotImplementedError
    
    def get_stocks(self, item):
        raise NotImplementedError
    
    def get_thumb_url(self, item):
        raise NotImplementedError
    
    def get_thumb_bytes(self, item):
        raise NotImplementedError

    def get_product_name(self, item):
        raise NotImplementedError
    
    def get_price(self, item):
        raise NotImplementedError

#Booth 
class BoothHandler(BaseHandler): 
    def __init__(self):
        super(BoothHandler, self).__init__()
        self.cookies = {'adult' : 't'}
    
    def get_item_list_from_soup(self, soup):
        return soup.select("#js-shop li[data-product-category='156']")
    
    def get_product_name(self, item):
        return item.find(class_ = 'item-name').select('a')[0].text
    
    def get_product_id(self, item):
        return item['data-product-id']
    
    def get_stocks(self, item):
        return 'No' if item.find(class_ = 'empty-stock') else 'Yes'
    
    def get_thumb_url(self, item):
        return item.find(class_ = 'swap-image').contents[0]['src']
    
    def get_price(self, item):
        return '¥' + item['data-product-price']
    
    def get_thumb_bytes(self, item):
        if GlobalSettings.download_thumb:
            if self.need_proxie:
                r = requests.get(self.get_thumb_url( item),
                                proxies = GlobalSettings.proxies)
            else:
                r = requests.get(self.get_thumb_url(item))
            return r.content
        else:
            return ""
 
#MelonBooks
class MelonHandler(BaseHandler): 
    def __init__(self):
        super(MelonHandler, self).__init__()
        self.cookies = {'AUTH_ADULT' : '1'}
    
    def get_item_list_from_soup(self, soup):
        return soup.select("div.layout_box.products.products_flex div.product")
    
    def get_product_name(self, item):
        return item.find('p', class_ = 'title').contents[0]['title']
    
    def get_product_id(self, item):
        pattern = "(?<=^product_)\\d+$"
        for cn in item['class']:
            m = re.search(pattern, cn)
            if m:
                return m.group(0)
        raise Exception("No id from melon")
    
    def get_stocks(self, item):
        return 'Yes'
    
    def get_price(self, item):
        return item.find('p', class_='price').find('em').text   
    
    def get_thumb_url(self, item):
        return "https:" + item.find(class_ = 'thumb').find('img')['data-src']
    
    def get_thumb_bytes(self, item):
        if GlobalSettings.download_thumb:
            if self.need_proxie:
                r = requests.get(self.get_thumb_url(item),
                                proxies = GlobalSettings.proxies)
            else:
                r = requests.get(self.get_thumb_url(item))
            return r.content
        else:
            return ""

site_handlers = {
    'Booth' : BoothHandler(),
    'Melon' : MelonHandler(),
}

def get_product_infos(shop_name, shop_url, sensei_name):    
    product_infos = site_handlers[shop_name].get_product_infos(shop_url)
    for info in product_infos:
        info.shop_name = shop_name
        info.sensei_name = sensei_name
    return product_infos
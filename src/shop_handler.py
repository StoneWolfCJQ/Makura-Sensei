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
        self.shop_url = ""        
        
    def get_product_infos(self, shop_url): 
        self.shop_url = shop_url
        item_list = []
        soup = self.get_product_soup(shop_url)
        pages = self.get_page_address(soup)
        item_list += self.get_item_list_from_soup(soup)
        if len(pages) > 0:
            for page in pages:
                soup = self.get_product_soup(page)
                item_list += self.get_item_list_from_soup(soup)
        product_infos = []
        for item in item_list:
            info = ProductInfo("", "", 
                               self.get_product_name(item),
                               self.get_product_id(item),
                               self.get_price(item),
                               self.get_stocks(item),
                               self.get_product_url(item),
                               self.get_thumb_url(item),
                               ""
                               )
            product_infos.append(info)
        return product_infos

    def get_product_soup(self, shop_url):
        proxies = GlobalSettings.proxies if self.need_proxie else None
        r = self.make_request(shop_url, proxies, self.cookies)
        '''if self.need_proxie:
            r = requests.get(shop_url, 
                         proxies = GlobalSettings.proxies, 
                         cookies = self.cookies)
        else:
            r = requests.get(shop_url, 
                         cookies = self.cookies)'''
            
        html = r.text
        soup = BeautifulSoup(html, 'lxml')
        return soup

    def make_request(self, url, proxies = None, cookies = None):
        return requests.get(url, proxies = proxies, cookies = cookies)
        
    def get_page_address(self, soup):
        raise NotImplementedError
        
    def get_item_list_from_soup(self, soup):
        raise NotImplementedError
    
    def get_product_id(self, item):
        raise NotImplementedError

    def get_product_name(self, item):
        raise NotImplementedError
    
    def get_price(self, item):
        raise NotImplementedError
    
    def get_stocks(self, item):
        raise NotImplementedError

    def get_product_url(self, item):
        raise NotImplementedError
    
    def get_thumb_url(self, item):
        raise NotImplementedError
    
    def get_thumb_bytes(self, item):
        return self.get_thumb_bytes(self.get_thumb_url(item))

    def get_thumb_bytes_url(self, url):
        if self.need_proxie:
            r = requests.get(url, proxies = GlobalSettings.proxies)
        else:
            r = requests.get(url)
        return r.content


#Booth 
class BoothHandler(BaseHandler): 
    def __init__(self):
        super(BoothHandler, self).__init__()
        self.cookies = {'adult' : 't'}
    
    def get_item_list_from_soup(self, soup):
        return soup.select("#js-shop li[data-product-category='156']")

    def get_page_address(self, soup):
        pages = soup.select("div.shop-pager a")
        pages_address = []
        if pages == None or len(pages) <= 0:
            return []
        else:
            for item in pages:
                if re.match('\\d+', item.text) and item.text != '1':
                    pages_address.append(self.shop_url + item['href'])
        return pages_address
    
    def get_product_name(self, item):
        return item.find(class_ = 'item-name').select('a')[0].text
    
    def get_product_id(self, item):
        return item['data-product-id']
    
    def get_stocks(self, item):
        return 'No' if item.find(class_ = 'empty-stock') else 'Yes'
    
    def get_price(self, item):
        return '¥' + item['data-product-price']

    def get_product_url(self, item):
        return self.shop_url + item.select('a[data-tracking="click_item"]')[0]['href']
    
    def get_thumb_url(self, item):
        return item.find(class_ = 'swap-image').contents[0]['src']
 
#MelonBooks
class MelonHandler(BaseHandler): 
    def __init__(self):
        super(MelonHandler, self).__init__()
        self.cookies = {'AUTH_ADULT' : '1'}
    
    def get_item_list_from_soup(self, soup):
        items = soup.select("div.products_flex div.product")  
        item_list = []
        for item in items:
            if item.find('span', class_ = 'gunre').find('span').text == "抱き枕カバー":
                item_list.append(item)
        return item_list

    def get_page_address(self, soup):
        return []
    
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

    def get_product_url(self, item):
        return "https://www.melonbooks.co.jp" + item.find(class_ = 'thumb').find('a')['href']
    
    def get_thumb_url(self, item):
        return "https:" + item.find(class_ = 'thumb').find('img')['data-src']

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

def fill_product_thumbs(senseis_products): 
    for sensei_name, products in senseis_products.items():
        for product in products:
            product.thumb_bytes = site_handlers[product.shop_name]\
                .get_thumb_bytes_url(product.thumb_url)

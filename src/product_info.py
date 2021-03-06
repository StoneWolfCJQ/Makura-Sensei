class ProductInfo():
    def __init__(self,
                 shop_name,
                 sensei_name,
                 product_name,
                 product_id,
                 price,
                 stocks,
                 product_url,   
                 thumb_url,
                 thumb_bytes = None):
        self.shop_name = shop_name
        self.sensei_name = sensei_name
        self.product_name = product_name
        self.product_id = product_id
        self.price = price
        self.stocks = stocks
        self.product_url = product_url
        self.thumb_url = thumb_url
        self.thumb_bytes = thumb_bytes
    
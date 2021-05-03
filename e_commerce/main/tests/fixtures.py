from datetime import datetime

import factory

from main.models import Category, Goods, Seller


class GoodsFactory(factory.Factory):
    class Meta:
        model = Goods

    name = "Test good"
    description = "Test good description"
    seller = Seller.objects.get(name="Bobbie's Bits")
    category = Category.objects.get(name="Tools")
    manufacturer = "Test manufacturer"
    price = 50
    creation_date = datetime.now()

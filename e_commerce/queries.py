from django.contrib.auth.models import Group, Permission
from main.models import Category, Goods, Seller, Tag

cat = Category(name="Toys")
cat.save()

Category.objects.create(name="Tools")
Category.objects.create(name="Hardware")
Soft = Category.objects.create(name="Software")

Tag.objects.create(name="New")
Tag.objects.create(name="Best Seller")
Tag.objects.create(name="Hammer")
Tag.objects.create(name="For Kids")

Seller.objects.create(
    name="Arse Tickler's Faggot Fan Club", rating=3, email="info@atffc.com"
)
Seller.objects.create(name="Bobbie's Bits", rating=5, email="bobby@bobbiesbits.com")

# Get sellers with rating more then 3
sellers = Seller.objects.filter(rating__gt=3)

Bobbeie = Seller.objects.get(rating=5)
tools = Category.objects.get(name="Tools")
Goods.objects.create(
    name="Hammer",
    description="Iron hammer. Keep your fingers safe",
    seller=Bobbeie,
    weight=0.3,
    category=tools,
    manufacturer="Noname",
    rating=5,
    price=10,
)

data_grip = Goods(
    name="DataGrip",
    description="IDE for DBs",
    seller=Bobbeie,
    weight=0,
    category=Soft,
    manufacturer="JetBrains",
    rating=4,
    price=80,
)
data_grip.save()


Hammer = Goods.objects.get(name="Hammer")
bs = Tag.objects.get(name="Best Seller")
ham_tag = Tag.objects.get(name="Hammer")
new = Tag.objects.get(name="New")
Hammer.tags.add(bs, ham_tag)


# Both goods filtred by price
goods_with_low_price = Goods.objects.filter(price__gte=10)

# Get all software

Software_goods = Goods.objects.filter(category=Soft)

sellers_group, created_grp = Group.objects.get_or_create(name="sellers")
add_goods = Permission.objects.get(name="Can add goods")
change_goods = Permission.objects.get(name="Can change goods")
sellers_group.permissions.add(add_goods, change_goods)

from django.contrib.auth.models import Group, Permission, User
from django.test import Client, TestCase
from django.urls import reverse_lazy
from django.utils.timezone import now

from main.models import Category, Goods, Profile, Seller, Subscriptions, Tag


class GoodsListTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def test_responce_status(self):
        response = self.client.get(reverse_lazy("goods"))
        self.assertEqual(response.status_code, 200)


class GoodsDetailTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        seller = Seller.objects.create(
            name="Bobbie's Bits", rating=5, email="bobby@bobbiesbits.com"
        )
        category = Category.objects.create(name="Tools")
        Subscriptions.objects.get_or_create(name="New goods")
        self.goods = Goods.objects.create(
            name="Hammer",
            description="Iron hammer. Keep your fingers safe",
            seller=seller,
            weight=0.3,
            category=category,
            manufacturer="Noname",
            rating=5,
            price=10,
            creation_date=now(),
        )

    def test_responce_status(self):
        response = self.client.get(
            reverse_lazy("goods-detail", kwargs={"pk": self.goods.id})
        )
        self.assertEqual(response.status_code, 200)


class GoodsCreateTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user("john", "lennon@qa.com", "johnpassword")
        sellers_group, created_grp = Group.objects.get_or_create(name="sellers")
        add_goods = Permission.objects.get(name="Can add goods")
        sellers_group.permissions.add(add_goods)
        sellers_group.user_set.add(self.user)

    def test_responce_status(self):
        self.client.login(username="john", password="johnpassword")
        response = self.client.get(reverse_lazy("goods-create"))
        self.assertEqual(response.status_code, 200)


class GoodsEditTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user("john", "lennon@qa.com", "johnpassword")
        sellers_group, created_grp = Group.objects.get_or_create(name="sellers")
        change_goods = Permission.objects.get(name="Can change goods")
        sellers_group.permissions.add(change_goods)
        sellers_group.user_set.add(self.user)
        seller = Seller.objects.create(
            name="Bobbie's Bits", rating=5, email="bobby@bobbiesbits.com"
        )
        category = Category.objects.create(name="Tools")
        Subscriptions.objects.get_or_create(name="New goods")
        self.goods = Goods.objects.create(
            name="Hammer",
            description="Iron hammer. Keep your fingers safe",
            seller=seller,
            weight=0.3,
            category=category,
            manufacturer="Noname",
            rating=5,
            price=10,
            creation_date=now(),
        )

    def test_responce_status(self):
        self.client.login(username="john", password="johnpassword")
        response = self.client.get(
            reverse_lazy("goods-edit", kwargs={"pk": self.goods.id})
        )
        self.assertEqual(response.status_code, 200)


class ProfileUpdateTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user("john", "lennon@qa.com", "johnpassword")

    def test_responce_status(self):
        self.client.login(username="john", password="johnpassword")
        response = self.client.get(reverse_lazy("profile", kwargs={"pk": self.user.id}))
        self.assertEqual(response.status_code, 200)


class IndexTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def test_responce_status(self):
        response = self.client.get(reverse_lazy("index"))
        self.assertEqual(response.status_code, 200)


class LoginTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user("john", "lennon@qa.com", "johnpassword")

    def testLogin(self):
        self.client.login(username="john", password="johnpassword")
        response = self.client.get(reverse_lazy("account_login"))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/")

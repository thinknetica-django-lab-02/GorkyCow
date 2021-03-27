from django.db import models


class Seller(models.Model):
    STATUSES = (
        ('A', 'Active'),
        ('P', 'Partner'),
        ('T', 'Test'),
        ('D', 'Disabled'),
    )
    name = models.CharField(max_length=80)
    status = models.CharField(max_length=1, choices=STATUSES, default='A')
    rating = models.FloatField()
    email = models.EmailField(max_length=254)


class Category(models.Model):
    name =  models.CharField(max_length=80)


class Tag(models.Model):
    name = models.CharField(max_length=80)


class Goods(models.Model):
    SIZES = (
        ('S', 'Small'),
        ('M', 'Medium'),
        ('L', 'Large'),
    )
    name = models.CharField(max_length=80)
    description = models.TextField()
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE, verbose_name="the related seller")
    weight = models.FloatField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, verbose_name="the related category", null=True)
    manufacturer = models.CharField(max_length=80)
    tags = models.ManyToManyField(Tag)
    size = models.CharField(max_length=1, choices=SIZES, null=True)
    rating = models.FloatField()

from django.db import models


class Seller(models.Model):
    STATUSES = (
        ("A", "Active"),
        ("P", "Partner"),
        ("T", "Test"),
        ("D", "Disabled"),
    )
    name = models.CharField(max_length=80)
    status = models.CharField(max_length=1, choices=STATUSES, default="A")
    rating = models.FloatField()
    email = models.EmailField(max_length=254)

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"Seller(name='{self.name}', status='{self.status}', rating={self.rating}, email='{self.email}')"


class Category(models.Model):
    name = models.CharField(max_length=80)

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"Category(name='{self.name}')"


class Tag(models.Model):
    name = models.CharField(max_length=80)

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"Tag(name='{self.name}')"


class Goods(models.Model):
    SIZES = (
        ("S", "Small"),
        ("M", "Medium"),
        ("L", "Large"),
    )
    name = models.CharField(max_length=80)
    description = models.TextField()
    seller = models.ForeignKey(
        Seller, on_delete=models.CASCADE, verbose_name="the related seller"
    )
    weight = models.FloatField()
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        verbose_name="the related category",
        null=True,
    )
    manufacturer = models.CharField(max_length=80)
    tags = models.ManyToManyField(Tag)
    size = models.CharField(max_length=1, choices=SIZES, null=True)
    rating = models.FloatField(default=5.0)
    price = models.FloatField(default=0)
    discount = models.FloatField(default=0, null=False)

    def __str__(self):
        return self.name

    def __repr__(self):
        return (
            f"Goods(name='{self.name}', description='{self.description}', seller={self.seller}, weight={self.weight}, "
            + f"category={self.category}, manufacturer='{self.manufacturer}', tags={self.tags.all()}, size='{self.size}', rating={self.rating}, price={self.price})"
        )

from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse


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

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def __repr__(self):
        return (
            f"Goods(name='{self.name}', description='{self.description}', seller={self.seller}, weight={self.weight}, "
            + f"category={self.category}, manufacturer='{self.manufacturer}', tags={self.tags.all()}, size='{self.size}', rating={self.rating}, price={self.price})"
        )


class Profile(models.Model):
    user = models.OneToOneField(
        User,
        auto_created=True,
        on_delete=models.CASCADE,
        parent_link=True,
        primary_key=True,
        serialize=False,
    )
    phone_regex = RegexValidator(
        regex=r"^\+?1?\d{9,15}$",
        message="Телефонный номер должен быть в формате: '+999999999' и не длиннее 15 символов.",
    )
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    birth_date = models.DateField(null=True, blank=True)

    def get_absolute_url(self):
        return reverse("profile", kwargs={"pk": self.pk})

    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            Profile.objects.create(user=instance)

    @receiver(post_save, sender=User)
    def save_user_profile(sender, instance, **kwargs):
        instance.profile.save()

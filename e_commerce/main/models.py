from django.contrib.auth.models import Group, User
from django.core.validators import RegexValidator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from sorl.thumbnail import ImageField

from main.messages import (new_goods_subscribers_notification,
                           send_welcome_email)


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
    weight = models.FloatField(null=True, blank=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        verbose_name="the related category",
        null=True,
    )
    manufacturer = models.CharField(max_length=80)
    tags = models.ManyToManyField(Tag)
    size = models.CharField(max_length=1, choices=SIZES, null=True, blank=True)
    rating = models.FloatField(default=5.0)
    price = models.FloatField(default=0)
    discount = models.FloatField(default=0, null=False)
    image = ImageField(upload_to="goods/", verbose_name="Фото", blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def __repr__(self):
        return (
            f"Goods(name='{self.name}', description='{self.description}', seller={self.seller}, weight={self.weight}, "
            + f"category={self.category}, manufacturer='{self.manufacturer}', tags={self.tags.all()}, size='{self.size}', rating={self.rating}, price={self.price}, "
            + f"image={self.image or None})"
        )


class Subscriptions(models.Model):
    name = models.CharField(max_length=80)

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"Subscriptions(name='{self.name}')"

    @receiver(post_save, sender=Goods)
    def goods_add_routine(sender, instance, created, **kwargs):
        if created:
            subscription = Subscriptions.objects.get(name="New goods")
            for profile in Profile.objects.filter(subsciber=subscription):
                new_goods_subscribers_notification(instance, profile)


class Profile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
    )
    phone_regex = RegexValidator(
        regex=r"^\+?1?\d{9,15}$",
        message="Телефонный номер должен быть в формате: '+999999999' и не длиннее 15 символов.",
    )
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    avatar = ImageField(upload_to="user_profile/", verbose_name="Аватар", blank=True)
    subsciber = models.ManyToManyField(
        Subscriptions, verbose_name="Подписки", blank=True
    )

    def get_absolute_url(self):
        return reverse("profile", kwargs={"pk": self.pk})

    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            common_users_group, created_grp = Group.objects.get_or_create(
                name="common_users"
            )
            instance.groups.add(common_users_group)
            Profile.objects.create(user=instance)
            send_welcome_email(instance)

    @receiver(post_save, sender=User)
    def save_user_profile(sender, instance, **kwargs):
        instance.profile.save()


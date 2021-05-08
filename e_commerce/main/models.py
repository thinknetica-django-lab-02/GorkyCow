from django.contrib.auth.models import Group, User
from django.contrib.postgres.fields import ArrayField
from django.core.validators import RegexValidator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from main.tasks import (send_new_goods_subscribers_notification_task,
                        send_welcome_email_task)
from picklefield.fields import PickledObjectField
from sorl.thumbnail import ImageField


class Seller(models.Model):
    """This class describes how to store and operate data about sellers.

    STATUSES - a tuple with possible statuses of a seller that using for
    choice in a status field
    name - a name of a seller
    status - a current status of a seller
    rating - a rating of a seller
    email - a contact email address of a seller
    """

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

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return (
            f"Seller(name='{self.name}', status='{self.status}', "
            + f"rating={self.rating}, email='{self.email}')"
        )


class Category(models.Model):
    """This class describes how to store and operate data about a Goods category.

    name - a name of a category
    """

    name = models.CharField(max_length=80)

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"Category(name='{self.name}')"


class Tag(models.Model):
    """This class describes how to store and operate data about tags.

    name - a name of a tag
    """

    name = models.CharField(max_length=80, unique=True)

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"Tag(name='{self.name}')"


class Goods(models.Model):
    """This class describes how to store and operate data about goods.

    SIZES - a tuple with possible sizes of a good that using for
    choice in a size field
    name - a name of a good
    description - a long text description which will be displayed in
    a detailed view
    seller - foreign key of a seller of this good
    weight - a weight of a good
    category - foreign key of a category of this good
    manufacturer - a manufacturer of this good
    tags - foreign keys of a tags of this good
    size - a size of this good
    rating - a current user's rating of a good
    price - a current price
    discount - a current discount provided by a seller
    image - a photo of this good
    creation_date - a date when a good had been created
    views_counter - a current views counter
    """

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
    tags = ArrayField(
        models.CharField(max_length=40, blank=True, null=True), blank=True, null=True
    )
    size = models.CharField(max_length=1, choices=SIZES, null=True, blank=True)
    rating = models.FloatField(default=5.0)
    price = models.FloatField(default=0)
    discount = models.FloatField(default=0, null=False)
    image = ImageField(upload_to="goods/", verbose_name="Фото", blank=True)
    creation_date = models.DateField(verbose_name="Дата создания")
    views_counter = models.IntegerField(default=0)
    in_stock = models.IntegerField(default=0)
    is_published = models.BooleanField(verbose_name="Опубликован", default=True)
    is_archive = models.BooleanField(verbose_name="В архиве", default=False)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return (
            f"Goods(name='{self.name}', description='{self.description}', "
            + f"seller={self.seller}, weight={self.weight}, "
            + f"category={self.category}, manufacturer='{self.manufacturer}'"
            + f", tags={self.tags}, size='{self.size}', "
            + f"rating={self.rating}, price={self.price}, "
            + f"image={self.image or None})"
        )


class Subscriptions(models.Model):
    """This class describes how to store and operate data about subscriptions.

    name - a name of a subscription
    """

    name = models.CharField(max_length=80)

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"Subscriptions(name='{self.name}')"

    @staticmethod
    @receiver(post_save, sender=Goods)
    def goods_add_routine(
        sender: Goods, instance: Goods, created: bool, **kwargs
    ) -> None:
        """This method creates delayed task which sents subscribed users
        an email about a newly created good.

        :param sender: Goods class
        :type sender: class 'main.models.Goods'
        :param instance: a newly created good object
        :type instance: class 'main.models.Goods'
        :param created: a boolean flag which indicates that an object was just
        created
        :type created: bool
        """
        if created:
            subscription = Subscriptions.objects.filter(name="New goods").first()
            if subscription:
                for profile in Profile.objects.filter(subsciber=subscription):
                    send_new_goods_subscribers_notification_task.delay(
                        instance.id, profile.id
                    )


class Profile(models.Model):
    """This class describes how to store and operate data about user's
    profiles.

    user - a foreign key of a user linked to this profile
    phone_regex - a regexp validator for phone number
    phone_number - a phone number for notifications
    is_phone_confirmed - a boolean flag which indicates that a phone number
    was confirmed
    birth_date - a bith date of a user
    avatar - user's uploaded profile pic
    subsciber - a foreign keys of user's subscriptions
    """

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
    )
    phone_regex = RegexValidator(
        regex=r"^\+?1?\d{9,15}$",
        message="Телефонный номер должен быть в формате: "
        + "'+999999999' и не длиннее 15 символов.",
    )
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    is_phone_confirmed = models.BooleanField(
        default=False, verbose_name="Телефон подтвержден"
    )
    birth_date = models.DateField(null=True, blank=True)
    avatar = ImageField(upload_to="user_profile/", verbose_name="Аватар", blank=True)
    subsciber = models.ManyToManyField(
        Subscriptions, verbose_name="Подписки", blank=True
    )

    def get_absolute_url(self) -> str:
        """This method returns an absolute URL to a user's profile.

        :return: a URL to a user's profile page
        :rtype: str
        """
        return reverse("profile", kwargs={"pk": self.pk})

    @staticmethod
    @receiver(post_save, sender=User)
    def create_user_profile(
        sender: User, instance: User, created: bool, **kwargs
    ) -> None:
        """This method creates a new linked Profile object when
        a user signs up.

        :param sender: User class
        :type sender: class 'django.contrib.auth.models'
        :param instance: a newly created user object
        :type instance: class 'django.contrib.auth.models'
        :param created: a boolean flag which indicates that an object was just
        created
        :type created: bool
        """
        if created:
            common_users_group, created_grp = Group.objects.get_or_create(
                name="common_users"
            )
            instance.groups.add(common_users_group)
            Profile.objects.create(user=instance)
            send_welcome_email_task.delay(instance.id)

    @staticmethod
    @receiver(post_save, sender=User)
    def save_user_profile(sender: User, instance: User, **kwargs) -> None:
        """This method saves a linked Profile object when
        a User object was updated.
        """
        instance.profile.save()


class SMSLog(models.Model):
    """This class describes how to store and operate data about sent messages
    and SMS gate responses.

    user - a foreign key of a user whom SMS was sent
    code - a generated code using for verification
    message - a server response
    creation_date - date and time when a message was sent
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    code = models.PositiveIntegerField()
    message = PickledObjectField()
    creation_date = models.DateTimeField(auto_now_add=True)


class GoodsShort(models.Model):
    """This class describes how to store and operate data about goods.

    name - a name of a good
    description - a long text description which will be displayed in
    a detailed view
    manufacturer - a manufacturer of this good
    tags - foreign keys of a tags of this good
    price - a current price
    creation_date - a date when a good had been created
    views_counter - a current views counter
    """

    class Meta:
        managed = False

    name = models.CharField(max_length=80)
    description = models.TextField()
    manufacturer = models.CharField(max_length=80)
    tags = ArrayField(
        models.CharField(max_length=40, blank=True, null=True), blank=True, null=True
    )
    price = models.FloatField(default=0)
    creation_date = models.DateField(verbose_name="Дата создания")
    views_counter = models.IntegerField(default=0)
    in_stock = models.IntegerField(default=0)
    is_published = models.BooleanField(verbose_name="Опубликован", default=True)
    is_archive = models.BooleanField(verbose_name="В архиве", default=False)

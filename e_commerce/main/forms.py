from datetime import date, datetime

from dateutil.relativedelta import relativedelta
from django import forms
from django.core.exceptions import ValidationError
from django.forms import inlineformset_factory, widgets
from django.utils.translation import gettext as _

from .models import Category, Goods, Profile, SMSLog, Subscriptions, Tag, User


class UserForm(forms.ModelForm):
    """This class describes a form that used to update a User object's fields."""

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email")
        labels = {
            "first_name": "Имя",
            "last_name": "Фамилия",
            "email": "Email",
        }


class ProfileForm(forms.ModelForm):
    """This class describes a form that used to update
    a Profile object's fields.
    """

    class Meta:
        model = Profile
        fields = "__all__"
        labels = {
            "phone_number": "Телефон",
            "birth_date": "Дата рождения",
            "subsciber": "Подписки",
        }
        widgets = {
            "birth_date": widgets.SelectDateWidget(
                years=range(datetime.now().year - 100, datetime.now().year + 1)
            ),
            "subsciber": widgets.SelectMultiple(choices=Subscriptions.objects.all()),
        }


class GoodsCreateUpdateForm(forms.ModelForm):
    """This class describes a form that used to create a Goods object
    or update an existing Goods object's fields.
    """

    class Meta:
        model = Goods
        fields = (
            "image",
            "name",
            "description",
            "weight",
            "category",
            "manufacturer",
            "tags",
            "size",
            "price",
            "discount",
        )
        labels = {
            "name": "Название",
            "description": "Описание",
            "weight": "Вес",
            "category": "Категория",
            "manufacturer": "Производитель",
            "tags": "Тэги",
            "size": "Размер",
            "price": "Цена",
            "discount": "Скидка",
        }
        widgets = {
            "description": widgets.Textarea(attrs={"cols": 60, "rows": 5}),
            "weight": widgets.NumberInput(),
            "category": widgets.Select(choices=Category.objects.all()),
            "tags": widgets.SelectMultiple(choices=Tag.objects.all()),
            "size": widgets.Select(),
            "price": widgets.NumberInput(),
            "discount": widgets.NumberInput(),
        }

    def clean_discount(self):
        """This method provides a custom check for the 'discount' field and
        raises an error if the discount more than 90%.
        """
        data = self.cleaned_data["discount"]
        if data > 90:
            raise ValidationError(
                _("Скидка не может быть больше 90 процентов. " + "Введено: %(value)s"),
                code="invalid",
                params={"value": data},
            )

        return data


class ProfileFormSet(
    inlineformset_factory(User, Profile, form=ProfileForm, can_delete=False)
):
    """This class describes a formset that used to combine the 'UserForm'
    and the 'ProfileForm' in one.
    """

    def __init__(self, *args, **kwargs):
        self.__initial = kwargs.pop("initial", [])
        super(ProfileFormSet, self).__init__(*args, **kwargs)

    def clean(self):
        """This method provides a custom check for the 'birth_date' field and
        raises an error if a user under 18 years old.
        """
        super(ProfileFormSet, self).clean()

        for form in self.forms:
            birth_date = form.cleaned_data.get("birth_date")

            if birth_date:
                today = date.today()
                if (today - relativedelta(years=18)) < birth_date:
                    msg = "Доступ к сайту разрешён лицам старше 18 лет"
                    form.add_error("birth_date", msg)
                    raise ValidationError(
                        _("Too young: %(value)s"),
                        code="invalid",
                        params={"value": birth_date},
                    )


class PhoneConfirmForm(forms.Form):
    """This class describes a form that used to confirm that
    a phone number exists.
    """

    code = forms.IntegerField()

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super(PhoneConfirmForm, self).__init__(*args, **kwargs)

    def clean_code(self):
        """This method provides a custom check for the 'code' field and raises
        an error if an inputted code mismatches a last sent to a user.
        """
        sms_log = (
            SMSLog.objects.filter(user=self.request.user)
            .order_by("creation_date")
            .last()
        )
        code = self.cleaned_data["code"]
        if code != sms_log.code:
            raise ValidationError(
                _("Введён неверный код: %(value)s"),
                code="invalid",
                params={"value": code},
            )
        else:
            profile = Profile.objects.get(user=self.request.user)
            profile.is_phone_confirmed = True
            profile.save()
        return code

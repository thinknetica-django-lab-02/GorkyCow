from datetime import date, datetime

from dateutil.relativedelta import relativedelta
from django import forms
from django.core.exceptions import ValidationError
from django.forms import inlineformset_factory, widgets
from django.utils.translation import gettext as _

from .models import Category, Goods, Profile, Tag, User


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "email")
        labels = {
            "first_name": "Имя",
            "last_name": "Фамилия",
            "email": "Email",
        }


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ("phone_number", "birth_date")
        labels = {
            "phone_number": "Телефон",
            "birth_date": "Дата рождения",
        }
        widgets = {
            "birth_date": forms.widgets.SelectDateWidget(),
        }


class GoodsCreateUpdateForm(forms.ModelForm):
    class Meta:
        model = Goods
        fields = (
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
            "description": forms.widgets.Textarea(attrs={"cols": 60, "rows": 5}),
            "weight": forms.widgets.NumberInput(),
            "category": forms.widgets.Select(choices=Category.objects.all()),
            "tags": forms.widgets.SelectMultiple(choices=Tag.objects.all()),
            "size": forms.widgets.Select(),
            "price": forms.widgets.NumberInput(),
            "discount": forms.widgets.NumberInput(),
        }

    def clean_discount(self):
        data = self.cleaned_data["discount"]
        if data > 90:
            raise ValidationError(
                _("Скидка не может быть больше 90 процентов. Введено: %(value)s"),
                code="invalid",
                params={"value": data},
            )

        return data


class ProfileFormSet(
    inlineformset_factory(
        User,
        Profile,
        fields=(
            "phone_number",
            "birth_date",
        ),
        can_delete=False,
        labels={
            "phone_number": "Телефон",
            "birth_date": "Дата рождения",
        },
        widgets={
            "birth_date": widgets.SelectDateWidget(
                years=range(datetime.now().year - 100, datetime.now().year + 1)
            ),
        },
    )
):
    def __init__(self, *args, **kwargs):
        self.__initial = kwargs.pop("initial", [])
        super(ProfileFormSet, self).__init__(*args, **kwargs)

    def clean(self):
        super(ProfileFormSet, self).clean()

        for form in self.forms:
            birth_date = form.cleaned_data.get("birth_date")

            if birth_date:
                today = date.today()
                # import pdb
                # pdb.set_trace()
                if (today - relativedelta(years=18)) < birth_date:
                    msg = "Доступ к сайту разрешён лицам старше 18 лет"
                    form.add_error("birth_date", msg)
                    raise ValidationError(
                        _("Too young: %(value)s"),
                        code="invalid",
                        params={"value": birth_date},
                    )

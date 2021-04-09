from datetime import date, datetime

from dateutil.relativedelta import relativedelta
from django import forms
from django.core.exceptions import ValidationError
from django.forms import inlineformset_factory, widgets
from django.utils.translation import gettext as _

from .models import Profile, User


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
        self.__initial = kwargs.pop('initial', [])
        super(ProfileFormSet, self).__init__(*args, **kwargs)

    def clean(self):
        super(ProfileFormSet, self).clean()

        for form in self.forms:
            birth_date = form.cleaned_data.get("birth_date")

            if birth_date:
                today = date.today()
                #import pdb
                #pdb.set_trace()
                if (today - relativedelta(years=18)) < birth_date:
                    msg = "Доступ к сайту разрешён лицам старше 18 лет"
                    form.add_error("birth_date", msg)
                    raise ValidationError(
                            _("Too young: %(value)s"),
                            code="invalid",
                            params={"value": birth_date},
                        )    

from ckeditor.widgets import CKEditorWidget
from django import forms
from django.contrib import admin
from django.contrib.flatpages.admin import FlatPageAdmin
from django.contrib.flatpages.models import FlatPage

from .models import Goods, Subscriptions


class FlatPageAdminForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorWidget())

    class Meta:
        model = FlatPage
        fields = "__all__"


class FlatPageAdmin(FlatPageAdmin):
    form = FlatPageAdminForm


class SubscriptionsAdmin(admin.ModelAdmin):
    list_display = ("name",)


class GoodsAdmin(admin.ModelAdmin):
    list_display = ("name",)


admin.site.register(Subscriptions, SubscriptionsAdmin)
admin.site.register(Goods, GoodsAdmin)
admin.site.unregister(FlatPage)
admin.site.register(FlatPage, FlatPageAdmin)

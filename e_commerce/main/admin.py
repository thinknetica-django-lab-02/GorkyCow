from ckeditor.widgets import CKEditorWidget
from django import forms
from django.contrib import admin
from django.contrib.flatpages.admin import FlatPageAdmin
from django.contrib.flatpages.models import FlatPage
from django.utils.html import format_html

from .models import Goods, Subscriptions, Tag


class FlatPageAdminForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorWidget())

    class Meta:
        model = FlatPage
        fields = "__all__"


class FlatPageAdmin(FlatPageAdmin):
    form = FlatPageAdminForm


class SubscriptionsAdmin(admin.ModelAdmin):
    list_display = ("name",)


def make_published(modeladmin, request, queryset):
    queryset.update(is_published=True)


make_published.short_description = "Public selected goods"


def make_unpublished(modeladmin, request, queryset):
    queryset.update(is_published=False)


make_unpublished.short_description = "Hide selected goods"


def make_archive(modeladmin, request, queryset):
    queryset.update(is_archive=True)


make_archive.short_description = "Add selected goods to archive"


def make_unarchive(modeladmin, request, queryset):
    queryset.update(is_archive=False)


make_unarchive.short_description = "Remove selected goods from archive"


class GoodsAdmin(admin.ModelAdmin):
    actions = [make_published, make_unpublished, make_archive, make_unarchive]
    list_display = (
        "id",
        "name",
        "description",
        "seller",
        "weight",
        "category",
        "manufacturer",
        "size",
        "rating",
        "price",
        "discount",
        "creation_date",
        "views_counter",
        "in_stock",
        "is_published",
        "is_archive",
    )
    list_filter = ("tags", "creation_date", "category")
    readonly_fields = ("get_image", "creation_date")
    search_fields = ("name", "description")
    list_editable = ("is_published", "is_archive")
    save_as = True
    save_on_top = True

    def get_image(self, obj):
        return format_html("<img src='{}' />".format(obj.image.url))

    get_image.short_description = "Изображение"


class TagAdmin(admin.ModelAdmin):
    list_display = ("name",)


admin.site.register(Subscriptions, SubscriptionsAdmin)
admin.site.register(Goods, GoodsAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.unregister(FlatPage)
admin.site.register(FlatPage, FlatPageAdmin)

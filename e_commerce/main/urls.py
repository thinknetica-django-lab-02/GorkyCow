from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from django.views.decorators.cache import cache_page

from . import views

urlpatterns = [
    path("", cache_page(60 * 15)(views.index), name="index"),
    path("goods/", views.GoodsList.as_view(), name="goods"),
    path(
        "phone_confirmation/",
        views.PhoneConfirmation.as_view(),
        name="phone-confirmation",
    ),
    path(
        "phone_confirmed/",
        views.PhoneConfirmed.as_view(),
        name="phone-confirmed"
    ),
    path("goods/<int:pk>/", views.GoodsDetail.as_view(), name="goods-detail"),
    path(
        "goods/create/",
        views.GoodsCreate.as_view(),
        name="goods-create",
    ),
    path(
        "goods/edit/<int:pk>/",
        views.GoodsUpdate.as_view(),
        name="goods-edit",
    ),
    path(
        "accounts/profile/<int:pk>/",
        views.ProfileUpdate.as_view(),
        name="profile",
    ),
    path("accounts/", include("allauth.urls")),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
    urlpatterns += static(
        settings.STATIC_URL,
        document_root=settings.STATIC_ROOT
    )

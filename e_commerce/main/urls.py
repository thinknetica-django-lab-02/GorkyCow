from django.contrib.auth.decorators import login_required
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("goods/", views.GoodsList.as_view(), name="goods"),
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
        login_required(views.ProfileUpdate.as_view()),
        name="profile",
    ),
    path("accounts/", include("allauth.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

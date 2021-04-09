from django.contrib.auth.decorators import login_required
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("goods/", views.GoodsList.as_view(), name="goods"),
    path("goods/<int:pk>/", views.GoodsDetail.as_view(), name="goods-detail"),
    path(
        "goods/create/",
        login_required(views.GoodsCreate.as_view()),
        name="goods-create",
    ),
    path(
        "goods/edit/<int:pk>/",
        login_required(views.GoodsUpdate.as_view()),
        name="goods-edit",
    ),
    path(
        "accounts/profile/<int:pk>/",
        login_required(views.ProfileUpdate.as_view()),
        name="profile",
    ),
]

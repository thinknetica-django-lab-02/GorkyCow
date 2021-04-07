from django.contrib.auth.decorators import login_required
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("goods/", views.GoodsList.as_view(), name="goods"),
    path("goods/<int:pk>/", views.GoodsDetail.as_view(), name="goods-detail"),
    path(
        "accounts/profile/<int:pk>/",
        login_required(views.ProfileUpdate.as_view()),
        name="profile",
    ),
]

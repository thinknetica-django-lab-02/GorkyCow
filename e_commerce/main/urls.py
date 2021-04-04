from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("goods/", views.GoodsList.as_view()),
    path('goods/<int:pk>/', views.GoodsDetail.as_view(), name='goods-detail'),
]

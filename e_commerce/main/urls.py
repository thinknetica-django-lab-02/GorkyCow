from django.conf import settings
from django.conf.urls.static import static
from django.contrib.flatpages.sitemaps import FlatPageSitemap
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path
from django.views.decorators.cache import cache_page
from django.views.generic.base import TemplateView
from main.sitemap import GoodsViewSitemap

from . import views

sitemaps = {
    "static": FlatPageSitemap,
    "goods": GoodsViewSitemap,
}

urlpatterns = [
    path("", cache_page(60 * 15)(views.index), name="index"),
    path("goods/", views.GoodsList.as_view(), name="goods"),
    path(
        "phone_confirmation/",
        views.PhoneConfirmation.as_view(),
        name="phone-confirmation",
    ),
    path("phone_confirmed/", views.PhoneConfirmed.as_view(), name="phone-confirmed"),
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
    path("search/", views.SearchView.as_view(), name="search"),
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    ),
    path(
        "robots.txt",
        TemplateView.as_view(
            template_name="main/robots.txt", content_type="text/plain"
        ),
    ),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

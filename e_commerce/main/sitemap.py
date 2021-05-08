from django.contrib.sitemaps import Sitemap
from main.models import Goods


class GoodsViewSitemap(Sitemap):
    changefreq = "daily"

    def items(self):
        return Goods.objects.all()

    def location(self, obj):
        return f"/goods/{obj.pk}/"

    def lastmod(self, obj):
        return obj.creation_date

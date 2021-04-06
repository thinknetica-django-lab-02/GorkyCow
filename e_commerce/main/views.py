from django.shortcuts import get_object_or_404, render
from django.views.generic import DetailView, ListView

from main.models import Goods, Tag


class GoodsList(ListView):
    model = Goods
    paginate_by = 9
    context_object_name = "goods_list"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tag_list"] = Tag.objects.all()
        context["tag"] = self.request.GET.get("tag")
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.GET.get("tag"):
            self.tag = get_object_or_404(Tag, name=self.request.GET.get("tag"))
            return queryset.filter(tags=self.tag)
        else:
            return queryset


class GoodsDetail(DetailView):
    queryset = Goods.objects.all()
    context_object_name = "goods"


def index(request):
    turn_on_block = True
    text_for_filter = "Братухе подари на днюху черный орфографический словарь"
    return render(
        request,
        "main/index.html",
        {
            "turn_on_block": turn_on_block,
            "user": request.user,
            "text_for_filter": text_for_filter,
        },
    )

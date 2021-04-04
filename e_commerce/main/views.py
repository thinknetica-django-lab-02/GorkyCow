from django.shortcuts import render
from django.views.generic import ListView, DetailView

from main.models import Goods, Tag


class GoodsList(ListView):
    model = Goods
    context_object_name = "goods"


class GoodsDetail(DetailView):
    queryset = Goods.objects.all()
    context_object_name = 'goods'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tag_list"] = Tag.objects.all()
        return context


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

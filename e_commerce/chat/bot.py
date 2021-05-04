from typing import Union

from asgiref.sync import sync_to_async
from main.models import Goods


async def process_message(message: str) -> str:
    if message.startswith("Наличие #"):
        good_name = message.replace("Наличие #", "")
        result = ["Вот что удалось найти:"]
        for good in await get_goods(good_name):
            if good.in_stock > 0:
                result.append(f"{good.name}. На складе осталось: {good.in_stock}")
            elif good.in_stock == 0:
                result.append(f"{good.name}. Товар закончился :(")
        if len(result) > 1:
            return "\n".join(result)
        else:
            return "Ничего не найдено"
    else:
        return "К сожалению, я не понял ваш запрос"


@sync_to_async
def get_goods(good_name: str) -> Union[Goods, None]:
    return list(Goods.objects.filter(name=good_name))

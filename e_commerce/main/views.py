from django.shortcuts import render


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

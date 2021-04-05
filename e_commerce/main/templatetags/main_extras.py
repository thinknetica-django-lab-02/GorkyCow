import datetime
from random import randint

from django import template

register = template.Library()


def swap_chars(word: str, first_char: int, second_char: int):
    if first_char > second_char:
        first_char += second_char
        second_char = first_char - second_char
        first_char -= second_char
    elif first_char == second_char:
        return word
    if first_char > len(word) - 1 or second_char > len(word) - 1:
        return word
    return (
        word[:first_char]
        + word[second_char]
        + word[first_char + 1 : second_char]
        + word[first_char]
        + word[second_char + 1 :]
    )


@register.filter(name="dyslexia", is_safe=True)
def dyslexia(value):
    if isinstance(value, str):
        return " ".join(
            [
                swap_chars(word, randint(1, len(word) - 2), randint(1, len(word) - 2))
                if len(word) > 3
                else word
                for word in value.split()
            ]
        )
    else:
        return value


@register.filter(name="revert", is_safe=True)
def revert(value):
    return value[::-1]


@register.simple_tag
def current_time(format_string):
    return datetime.datetime.now().strftime(format_string)

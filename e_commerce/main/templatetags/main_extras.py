import datetime
from random import randint

from django import template

register = template.Library()


def swap_chars(word: str, first_char: int, second_char: int):
    """This function swaps 'first_char' and 'second_char' in a given 'word'.

    :param word: a word where chars will be swapped
    :type word: str
    :param first_char: position of a first char
    :type first_char: int
    :param second_char: position of a second char
    :type second_char: int
    """
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
        + word[first_char + 1:second_char]
        + word[first_char]
        + word[second_char + 1:]
    )


@register.filter(name="dyslexia", is_safe=True)
def dyslexia(value):
    """This function swaps two random chars in all words of a given string.

    :param value: input string
    :type value: str
    """
    if isinstance(value, str):
        return " ".join(
            [
                swap_chars(
                    word,
                    randint(1, len(word) - 2),
                    randint(1, len(word) - 2)
                )
                if len(word) > 3
                else word
                for word in value.split()
            ]
        )
    else:
        return value


@register.filter(name="addclass")
def addclass(value, arg):
    """This function adds a CSS class to a given HTML tag.

    :param value: a tag in which a CSS class will be added
    :type value: class 'django.forms.boundfield.BoundField'
    :param arg: CSS class name
    :type arg: str
    """
    return value.as_widget(attrs={"class": arg})


@register.filter(name="revert", is_safe=True)
def revert(value):
    """This function reverts a given string.

    :param value: a string which will be reverted
    :type value: str
    """
    return value[::-1]


@register.simple_tag
def current_time(format_string):
    """This function returns the current server time in a given string format.

    :param format_string: a string that provides how-to format time
    :type format_string: str
    """
    return datetime.datetime.now().strftime(format_string)

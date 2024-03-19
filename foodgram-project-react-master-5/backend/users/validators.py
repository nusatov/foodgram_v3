import re

from rest_framework.serializers import ValidationError

PATTERN = r'^[\w.@+-]+\Z'


def username_validation(value):
    """
    Нельзя использовать имя пользователя me.
    Допускается использовать только буквы, цифры и символы @ . + - _.
    """

    uniq_simbols = ''.join(set(value))
    checked_value = re.sub(PATTERN, '', uniq_simbols)

    if checked_value:
        raise ValidationError(f'Нельзя использовать символы {checked_value} '
                              'Имя пользователя может содержать '
                              'только буквы, цифры и символы @ . + - _.')
    return value

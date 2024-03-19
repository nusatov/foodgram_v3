from enum import Enum, IntEnum


class UserMaxLength(IntEnum):
    """Максимальная длина полей пользователя."""

    USERNAME = 150
    EMAIL = 254
    FIRST_NAME = 150
    LAST_NAME = 150
    PASSWORD = 150


class TagMaxLength(IntEnum):
    """Максимальная длина полей тега."""

    NAME = 200
    COLOR = 7
    SLUG = 200


class IngredientMaxLength(IntEnum):
    """Максимальная длина полей ингредиента."""

    NAME = 200
    MEASUREMENT_UNIT = 200


class RecipeMaxLength(IntEnum):
    """Максимальная длина полей рецепта."""

    NAME = 200
    TEXT = 200


class ImageMaxSize(Enum):
    """Максимальная длина полей изображения."""

    IMAGE_SIZE = 500, 500


class RecipeCookingTime(IntEnum):
    MAX = 32000
    MIN = 1


class RecipeAmount(IntEnum):
    MIN = 1

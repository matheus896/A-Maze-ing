import random


class Color:
    RESET = "\033[0m"

    COLORS = (
        "\033[31m",  # Red
        "\033[32m",  # Green
        "\033[33m",  # Yellow
        "\033[34m",  # Blue
        "\033[35m",  # Magenta
        "\033[36m",  # Cyan
        "\033[37m",  # White
    )

    @staticmethod
    def pick_color():
        return random.choice(Color.COLORS)
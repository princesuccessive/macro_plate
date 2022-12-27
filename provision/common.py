from functools import partial

from termcolor import colored

green = partial(colored, color='green')
red = partial(colored, color='red')


def message(text):
    """Format message
    Args:
        text (str): textual message to format
    """
    length = len(text) if len(text) > 76 else 76

    msg = "\n"
    msg += "o" * (length + 4) + "\n"
    msg += "o {:76s} o\n".format(text)
    msg += "o" * (length + 4) + "\n"
    return msg


def print_green(msg):
    return print(green(message(msg)))


def print_red(msg):
    return print(green(message(msg)))

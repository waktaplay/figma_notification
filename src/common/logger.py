from enum import Enum


class Color(Enum):
    RESET = "\x1b[0m"
    RED = "\x1b[31m"
    GREEN = "\x1b[32m"


class Logger:
    @staticmethod
    def debug(text, color: Color = Color.GREEN):
        print(f"{color.value}[Crawler]{Color.RESET.value} {text}", flush=True)

    def error(self, error: str):
        print(f"{Color.RED.value}[Crawler]{Color.RESET.value} {error}", flush=True)
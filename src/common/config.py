import json
import sys
from enum import Enum, auto
from pathlib import Path


class Env(Enum):
    PROD = auto()
    DEV = auto()


def _load_json(path: str) -> dict:
    path = config_dir_path.joinpath(path)
    with open(path, mode="r", encoding="utf-8-sig") as f:
        return json.load(f)


def _to_path(filename: str):
    return config_dir_path.joinpath(filename)


env = Env.PROD if "--prod" in sys.argv else Env.DEV
config_dir_path = Path(__file__).parent.parent.parent.joinpath("config")

config_path = _to_path("dev-config.json" if env == Env.DEV else "config.json")
config = _load_json(config_path)

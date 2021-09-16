import json
from tortoise import Tortoise
from typing import Optional

from config import DB_URL, REQUEST_DATA_FILE


async def connect_db() -> None:
    await Tortoise.init(db_url=DB_URL, modules={"models": ["models"]})


async def read_json() -> dict:
    with open(REQUEST_DATA_FILE) as f:
        requests: dict = json.load(f)
    return requests


def find_node(nodes: list, key: str) -> Optional[dict]:
    try:
        return next(n for n in nodes if n["key"] == key)
    except StopIteration:
        return None

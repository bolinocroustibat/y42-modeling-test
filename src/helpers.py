import json
from typing import Optional

from tortoise import Tortoise

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


def sort_edges(edges: list) -> list:
    """
    Sort the edges in the edges list.
    """
    edges.sort(key=lambda e: e["from"])
    edges.sort(key=lambda e: e["to"])
    return edges

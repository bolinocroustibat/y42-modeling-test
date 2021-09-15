import asyncio
import json
from tortoise import Tortoise
from tortoise.functions import Count, Trim, Lower, Upper, Coalesce
from tortoise.query_utils import Q
from typing import Optional

from config import DB_MODELS, DB_URL, REQUEST_DATA_FILE
from models import *


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


class NodeQuery:

    def __init__(self, transform: dict) -> None:
        self.__call__(type="INPUT", transform=transform)

    def __call__(self, type: str, transform: dict) -> None:
        if type == "INPUT":
            self.input(transform)
        elif type == "FILTER":
            self.filter(transform)
        elif type == "SORT":
            self.sort(transform)
        elif type == "TEXT_TRANSFORMATION":
            self.text_transform(transform)
        elif type == "OUTPUT":
            self.output(transform)
        
    def input(self, transform: dict) -> None:
        table_name: str = transform["tableName"]
        select_fields: list[str] = transform["fields"]
        self.query = DB_MODELS[table_name].all().only(*select_fields)

    def filter(self, transform: dict) -> None:
        # TODO
        # if transform["joinOperator"] == "AND":
        #     q_objects: list = [None]
        #     for o in transform["operations"]:
        #         q_objects.add(Q(name='zob'))
        # elif transform["joinOperator"] == "OR":
            pass
    
    def sort(self, transform: dict) -> None:
        for t in transform:
            if t["order"] == "ASC":
                self.query = self.query.order_by(t["target"])
            elif t["order"] == "DESC":
                self.query = self.query.order_by("-" + t["target"])
    
    def text_transform(self, transform: dict) -> None:
        # TODO
        for t in transform:
            self.query = self.query.annotate(name_upper=Upper('name'))
        pass

    def output(self, transform: dict) -> None:
        self.query = self.query.limit(transform["limit"]).offset(transform["offset"])


async def main() -> None:

    await connect_db()

    requests = await read_json()
    nodes: dict = requests["nodes"]
    edges: dict = requests["edges"]

    # Initial node, create the initial query
    current_key: str = edges[0]["from"]
    node = find_node(nodes=nodes, key=current_key)
    if node["type"] != "INPUT": raise Exception("First node must be INPUT!")
    node_query = NodeQuery(transform=node["transformObject"])

    # Following nodes
    for e in edges:
        if e["from"] == current_key:
            node: Optional[dict] = find_node(nodes=nodes, key=e["to"])
            if node:
                node_query(type=node["type"], transform=node["transformObject"])
            current_key = e["to"]

    # Execute the final query at once
    users: list = await node_query.query
    for u in users: print(u)


if __name__ == "__main__":
    asyncio.run(main())
    print("Script executed, you can quit with CTRL+C.")

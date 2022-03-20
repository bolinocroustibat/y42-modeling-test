import asyncio
from typing import Optional

from tortoise import Tortoise

from helpers import connect_db, find_node, read_json, sort_edges


class NodeQuery:
    """
    NodeQuery class represents a query to be executed on the database, with its method to modify it.
    Initalization is the same as input method.
    """

    VALID_COLUMNS = {"users": ["id", "age", "name"]}

    def __init__(self, type: str, transform: dict) -> None:
        if type != "INPUT":
            raise Exception("First node must be INPUT!")
        self.__call__(type="INPUT", transform=transform)

    def __call__(self, type: str, transform: dict) -> None:
        if type == "INPUT":
            self._input(transform)
        elif type == "FILTER":
            self._filter(transform)
        elif type == "SORT":
            self._sort(transform)
        elif type == "TEXT_TRANSFORMATION":
            self._text_transform(transform)
        elif type == "OUTPUT":
            self._output(transform)

    def _validate_column(self, column_name: str) -> None:
        if column_name not in self.VALID_COLUMNS[self.table]:
            raise Exception(
                f"Column '{column_name}' doesn't exist in table '{self.table}'"
            )

    def _input(self, transform: dict) -> None:
        self.table: str = transform["tableName"]
        self.columns: list[str] = transform["columns"]
        for c in self.columns:
            self._validate_column(c)
        self.query: str = "SELECT " + ", ".join(self.columns) + " FROM " + self.table

    def _filter(self, transform: dict) -> None:
        query_part: str = ""
        self._validate_column(transform["column"])
        for o in transform["operations"]:
            if query_part:
                query_part += " AND "
            query_part += transform["column"] + " " + o["operator"] + " " + o["value"]
        self.query = "SELECT * FROM (" + self.query + ") WHERE " + query_part

    def _sort(self, transform: dict) -> None:
        query_part: str = ""
        for t in transform:
            self._validate_column(t["column"])
            if query_part:
                query_part += ", "
            query_part += t["column"] + " " + t["order"]
        self.query = "SELECT * FROM (" + self.query + ") ORDER BY " + query_part

    def _text_transform(self, transform: dict) -> None:
        query_part_1: str = ""
        not_transformed_columns = self.columns
        for t in transform:
            self._validate_column(t["column"])
            if query_part_1:
                query_part_1 += ", "
            query_part_1 += (
                t["transformation"] + "(" + t["column"] + ") AS " + t["column"]
            )
            not_transformed_columns.remove(t["column"])
        query_part_2: str = ""
        if not_transformed_columns:
            query_part_2 = ", " + ", ".join(not_transformed_columns)
        self.query = (
            "SELECT " + query_part_1 + query_part_2 + " FROM (" + self.query + ")"
        )

    def _output(self, transform: dict) -> None:
        self.query = (
            "SELECT * FROM ("
            + self.query
            + ") LIMIT "
            + str(transform["offset"])
            + ", "
            + str(transform["limit"])
        )

    async def execute_query(self) -> list[dict]:
        connection = Tortoise.get_connection("default")
        return await connection.execute_query_dict(self.query)


async def main() -> None:
    """
    The main function of the script.
    """
    await connect_db()

    # Parse the input JSON file
    requests = await read_json()
    nodes: list = requests["nodes"]
    edges: list = sort_edges(edges=requests["edges"])

    # Initial node, instanciate the initial query object
    current_key: str = edges[0]["from"]
    node: Optional[dict] = find_node(nodes=nodes, key=current_key)
    node_query = NodeQuery(type=node["type"], transform=node["transformObject"])

    # Following nodes
    for e in edges:
        if e["from"] == current_key:
            node: Optional[dict] = find_node(nodes=nodes, key=e["to"])
            if node:
                node_query(type=node["type"], transform=node["transformObject"])
            current_key = e["to"]

    # Evaluate the final query and get the results
    users = await node_query.execute_query()
    for u in users:
        print(u)


if __name__ == "__main__":
    asyncio.run(main())
    print("Script executed, you can quit with CTRL+C.")

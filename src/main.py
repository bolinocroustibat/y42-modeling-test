import asyncio
from typing import Optional

from helpers import connect_db, find_node, read_json, sort_edges
from query import NodeQuery


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
    if node:
        node_query = NodeQuery(type=node["type"], transform=node["transformObject"])
    else:
        raise Exception(f"No node found for key {current_key}")

    # Following nodes
    for e in edges:
        if e["from"] == current_key:
            node = find_node(nodes=nodes, key=e["to"])
            if node:
                node_query(type=node["type"], transform=node["transformObject"])
            else:
                raise Exception(f"No node found for key {current_key}")
            current_key = e["to"]

    # Evaluate the final query and get the results
    users: list[dict] = await node_query.execute_query()
    for u in users:
        print(u)


if __name__ == "__main__":
    asyncio.run(main())
    print("Script executed, you can quit with CTRL+C.")

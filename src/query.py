from tortoise import Tortoise


class NodeQuery:
    """
    NodeQuery class represents a query to be executed on the database, with its methods to modify it from the nodes.
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
        else:
            raise Exception("Unknown type transformation.")

    async def execute_query(self) -> list[dict]:
        connection = Tortoise.get_connection("default")
        return await connection.execute_query_dict(self.query)

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
        not_transformed_columns: list = self.columns
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

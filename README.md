# Prerequisites

You need:
- Python 3.9 (not tested below 3.9, but it should be fine with 3.8)
- [Poetry](https://python-poetry.org/) (Python packaging manager)

An example SQLite database is provided in the repo.


# To run

Edit the config file `/src/config.py`to change the database or the JSON file if necessary. Then, to run, just do:
```sh
poetry run python src/main.py
```
Poetry will create the virtual environment and install the necessary packages in it for you.


# File structure

- `/data/`
	- `db.sqlite3`: the example SQLite DB, with a `users` table with a few example rows
	- `request-data.json`: the input JSON

- `/src/`
	- `main.py`: the main function of the script, where everything starts
	- `query.py`: query class that holds the logic to build a SQL query object from the transformation objects, used by `main.py` 
	- `config.py`: configuration file to be edited
	- `models.py`: ORM class models for corresponding DB tables (not used in this example)
	- `helpers.py`: secondary helper functions used by `main.py`


# Original task

- Parse `request-data.json` into the query similar to `result.sql`. 

Inside `request-data.json` you have two properties `nodes` and `edges`, `nodes` contains all the required information to apply the transformation into Table/Query and `edges` represents how they are linked together. In each node there is a property `transformObject` which is different for each `type`
There are 5 different types of nodes used in this request

	- INPUT		-> it contains information about table and which fields to select from original table. 
	- FILTER	-> contains SQL "where" settings 
	- SORT		-> contains SQL "order by" settings 
	- TEXT_TRANSFORMATION	    -> contains information about applying some text SQL function on any column. For example UPPER, LOWER (see the digram for actual use case)
	- OUTPUT	-> contains SQL "limit" settings

Graphical representation of actual use-case:
![graphical representation](https://github.com/goes-funky/modeling-test/blob/master/graphical-representation.png?raw=true)

Use your imagination to fill in the missing information however you like to achieve the result.

## Bonus Points

 - Optimize `request-data.json` json structure/schema. EDIT: the JSON schema has been slightly changed using consistent key names for better consistency and readability.
 - Extendable structure which allows to add more types easily in the future. EDIT: it's easy to add a type, just need to add a method to the `NodeQuery` class.
 - Suggestion on how to validate the columns used inside the nodes. EDIT: the `NodeQuery` class hold a private `_validate_column` method which is used to validate the columns used inside the nodes.

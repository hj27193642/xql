from typing import List
from fastapi import FastAPI, Depends, HTTPException

from starlette_graphene3 import GraphQLApp, make_graphiql_handler
from starlette.middleware.cors import CORSMiddleware

from time import time
from datetime import datetime, timedelta

from schema import schemaQry
from database import RELOAD_DIRS
"""
 * @package xql
 * @date 2024-01-14
 * 
 * @history
 * 2024-01-28 service
 *
 * @
 * ├── src
 * │   ├── database.py
 * │   ├── __init__.py
 * │   ├── main.py
 * │   ├── model.json
 * │   ├── model.py
 * │   ├── resolver.py
 * │   ├── schema.py
 * │   └── utilitys.py
 * │
 * ├── .env
 * ├── poetry.lock
 * ├── pyproject.toml
 * ├── README.md
 * └── tests
"""





# logX ("Create All", loger, "INFO")

app = FastAPI()

app.add_middleware(
	CORSMiddleware,
	allow_origins=["*"],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)


# Apply GraphQL uri path 
app.add_route("/graphql", GraphQLApp(schema=schemaQry  ))
# ,on_get=make_graphiql_handler()
if __name__ == "__main__":
	import uvicorn

	# FastAPI application running
	uvicorn.run('main:app', host="0.0.0.0", port=8080,access_log=True, reload_dirs=[RELOAD_DIRS], reload=True,workers=16 )


import sqlite3
# from urllib.parse import urlencode
from functools import lru_cache

import uvicorn

from starlette.applications import Starlette
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route, Mount
from starlette.staticfiles import StaticFiles


query_str = """
    SELECT
    year,
    title,
    author,
    snippet(articles_fts, 5, '<b>', '</b>', '...', 60) text
    FROM
    articles_fts
    WHERE
    articles_fts = '' || ? || ''
    and year is not NULL
    ORDER BY :sort: :direction:
    LIMIT cast(? as int) OFFSET cast(? as int)
"""


def get_connection() -> sqlite3.Connection:
    return sqlite3.connect("file:historisk-samfund.db?mode=ro", uri=True)


def startup():
    print('Startup-function called')


def shutdown():
    print('Shutdown-function called')


@lru_cache(maxsize=16)
def get_total_hits(q: str, year: str = None) -> int:
    conn = get_connection()
    where_clause = "WHERE articles_fts = ?"
    if year: where_clause += f" and year = {year}"
    total: tuple = conn.execute(f"SELECT COUNT(*) FROM articles_fts {where_clause}", (q,)).fetchone()
    return int(total[0])


def search_articles(request: Request):
    conn = get_connection()
    q: str = request.query_params["q"]
    year: str = request.query_params.get("year")
    sort: str = request.query_params.get("sort", "year")
    if sort.lower() not in ["title_desc", "title_asc", "year_desc", "year_asc", "author_asc", "author_desc"]:
        sort = "year_asc"
    direction: str = request.query_params.get("direction", "asc")
    if direction.lower() not in ["asc", "desc"]:
        direction = "asc"
    size = int(request.query_params.get("size", 20))
    offset = int(request.query_params.get("offset", 0))
    total: int = get_total_hits(q, year)

    # get result-rows
    if year and 1908 <= int(year) <= 2014:
        query_str2 = query_str.replace("year is not NULL", f"year = {year}")
        prepared_stmt: str = query_str2.replace(":sort:", sort.split("_")[0]).replace(":direction:", sort.split("_")[1])
    else:
        prepared_stmt: str = query_str.replace(":sort:", sort.split("_")[0]).replace(":direction:", sort.split("_")[1])

    rows: list[dict] = []
    for row in conn.execute(prepared_stmt, (q, size, offset,)):
        rows.append({
            "year": row[0],
            "title": row[1],
            "author": row[2],
            "snippet": row[3]
        })

    out = {
        "q": q,
        "size": size,
        "sort": sort,
        "offset": offset,
        "rows": rows,
        "total": total
    }

    # if the optional year-filter is present, add it to output
    if year: out["year"] = int(year)

    # hvis offset plus size er mindre en total, så kan vi gå videre
    if offset + size < int(total):
        if "offset" not in request.url.query:
            out["next"] = f"{request.url.query}&offset={offset + size}"
        else:
            out["next"] = request.url.query.replace(f"offset={offset}", f"offset={offset + size}")

    # hvis vi er offset mere end size, så kan vi gå tilbage
    if offset - size >= 0:
        if "offset" not in request.url.query:
            out["previous"] = f"{request.url.query}&offset={offset - size}"
        else:
            out["previous"] = request.url.query.replace(f"offset={offset}", f"offset={offset - size}")

    return JSONResponse(out)


async def http_exception(request: Request, exc: HTTPException):
    return JSONResponse(
        {"detail": exc.detail},
        status_code=exc.status_code,
        headers=exc.headers
    )

routes = [
    Route("/search", endpoint=search_articles, methods=["GET"]),
    Mount('/static', app=StaticFiles(directory='statics'), name='static')
]

exception_handlers = {
    HTTPException: http_exception
    # 404: not_found,
    # 500: server_error
}

app = Starlette(
    routes=routes,
    on_startup=[startup],
    on_shutdown=[shutdown],
    debug=True,
    exception_handlers=exception_handlers
)

if __name__ == "__main__":
    uvicorn.run(app, host='0.0.0.0', port=8000)
import sqlite3
import csv
import sys


def main():
    # Increase CSV field size limit to maximim possible
    # https://stackoverflow.com/a/15063941
    field_size_limit = sys.maxsize
    while True:
        try:
            csv.field_size_limit(field_size_limit)
            break
        except OverflowError:
            field_size_limit = int(field_size_limit / 10)

    articles: list[tuple]
    with open('histsamf_articles.csv', 'r', encoding="utf-8") as f:
        dr = csv.DictReader(f)
        articles = [(i['author'], i['year'], i['pages'], i['title'], i['place'], i['tags'], i['data'], i['filename']) for i in dr]
    
    con = sqlite3.connect("db.db")
    cur = con.cursor()
    with open('schema.sql') as fp:
        cur.executescript(fp.read())
    cur.executemany(
        "insert into articles (author, year, pages, title, place, tags, data, filename) VALUES (?, ?, ?, ?, ?, ?, ?, ?);", articles)
    con.commit()

if __name__ == "__main__":
    main()

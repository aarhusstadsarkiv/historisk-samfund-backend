BEGIN TRANSACTION;

CREATE TABLE IF NOT EXISTS "articles" (
  "id" INTEGER,
  "author" TEXT,
  "year" INTEGER,
  "pages" TEXT,
  "title" TEXT,
  "place" TEXT,
  "tags" TEXT,
  "data" TEXT,
  "file_id" INTEGER,
  "filename" TEXT,
  PRIMARY KEY("id")
);

CREATE VIRTUAL TABLE "articles_fts" USING FTS5(
  author,
  year,
  pages,
  title,
  place,
  tags,
  data,
  filename,
  detail = full,
  content_rowid = 'id',
  content = 'articles',
  -- This syntax works!
  tokenize="unicode61 remove_diacritics 2 tokenchars '-_'"
);

CREATE TRIGGER after_articles_insert
AFTER
INSERT ON articles BEGIN
INSERT INTO articles_fts (
    rowid,
    author,
    year,
    pages,
    title,
    place,
    tags,
    data,
    filename
  )
VALUES
  (
    new.id,
    new.author,
    new.year,
    new.pages,
    new.title,
    new.place,
    new.tags,
    new.data,
    new.filename
  );
END;
COMMIT;

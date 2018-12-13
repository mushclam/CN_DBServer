DROP TABLE IF EXISTS article;

CREATE TABLE article (
    id INTEGER PRIMARY KEY,
    type TEXT NOT NULL,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    time DATETIME NOT NULL,
    body TEXT,
    CHECK (type in ('normal', 'notice'))
);

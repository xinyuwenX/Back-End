/* SQLite schema for creating 4 tables */

PRAGMA foreign_keys = ON;

create table articles (
 id integer primary key autoincrement,
 url text,
 text text,
 title text,
 author text,
 timestamp_create text,
 timestamp_modified text
);

create table tags (
 id integer primary key autoincrement,
 tag text,
 url text,
 foreign key (url) references articles (url)
);

create table comments (
 id integer primary key autoincrement,
 comment text,
 url text,
 author text,
 date text,
 foreign key (url) references articles (url)
);

create table users (
 id integer primary key autoincrement,
 name text,
 email text,
 password text
);
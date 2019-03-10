/* SQLite schema for creating 4 tables */

create table articles (
 url text primary key,
 text text,
 title text,
 author text,
 timestamp_create text,
 timestamp_modified text
);

create table tags (
 id integer primary key,
 tag text,
 url text,
 foreign key (url) references articles (url)
);

create table comments (
 id integer primary key,
 comment text,
 url text,
 author text,
 date text,
 foreign key (url) references articles (url)
);

create table users (
 id int primary key,
 name text,
 email text,
 password text
);
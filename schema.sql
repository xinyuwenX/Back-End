/* SQLite schema for creating 4 tables */
/* Author: Xinyu Wen*/

PRAGMA foreign_keys = ON;

drop table if exists articles;
drop table if exists tags;
drop table if exists comments;
drop table if exists users;

create table articles (
 id integer primary key autoincrement,
 url text unique not null,
 content text not null,
 title text not null,
 author text not null,
 timestamp_create text not null,
 timestamp_modified text not null
);

create table tags (
 id integer primary key autoincrement,
 tag text not null,
 url text not null,
 foreign key (url) references articles (url)
);

create table comments (
 id integer primary key autoincrement,
 comment text not null,
 url text not null,
 author text not null,
 date text not null,
 foreign key (url) references articles (url)
);

create table users (
 id integer primary key autoincrement,
 name text not null,
 email text unique not null,
 password text not null
);
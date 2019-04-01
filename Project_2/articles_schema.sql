/* Project 2 */
/* SQLite schema for creating articles table */

drop table if exists articles;

create table articles (
 id integer primary key autoincrement,
 url text unique not null,
 content text not null,
 title text not null,
 author text not null,
 timestamp_create text not null,
 timestamp_modified text not null
);
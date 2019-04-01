/* Project 2 */
/* SQLite schema for creating comments table */

drop table if exists comments;

create table comments (
 id integer primary key autoincrement,
 comment text not null,
 url text not null,
 author text not null,
 date text not null,
);
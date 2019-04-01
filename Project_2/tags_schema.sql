/* Project 2 */
/* SQLite schema for creating users table */

drop table if exists tags;

create table tags (
 id integer primary key autoincrement,
 tag text not null,
 url text not null,
);
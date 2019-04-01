/* Project 2 */
/* SQLite schema for creating users table */

drop table if exists users;

create table users (
 id integer primary key autoincrement,
 name text not null,
 email text unique not null,
 password text not null
);
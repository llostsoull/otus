create table users
(
    id           bigserial primary key,
    username    varchar(250),
    first_name   varchar(250),
    last_name    varchar(250),
    email       varchar(250),
    phone       varchar(250),
    created_at timestamp without time zone not null default now(),
    updated_at timestamp without time zone not null default now(),
    deleted    boolean                     not null default false
)with (oids = false);


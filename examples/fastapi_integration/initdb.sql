begin;


create extension if not exists "uuid-ossp";


create table if not exists "users"
(
    "id" uuid default uuid_generate_v4(),
    "created_at" timestamptz not null default now(),
    "updated_at" timestamptz not null default now(),
    "login" varchar unique not null,
    "password" varchar not null,
    "role" varchar not null,
    primary key ("id")
);


insert into "users"
(
    "login",
    "password",
    "role"
)
values
(
    'admin',
    'admin',
    'admin'
),
(
    'employee',
    'employee',
    'employee'
);


commit;

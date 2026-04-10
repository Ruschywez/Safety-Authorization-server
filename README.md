## Safety Authorization (Server)
It's a simple project for self-learning, created with the goal of learning "how to create a safe API".

When I was creating systems in the past, they were really simple and unsafe.

The main problem with my systems was trusting the client too much. Servers never checked users' rights and anyone could access any information from the backend, just by using simple HTTP requests with a different ID.

For example, my other projects that have this problem:

- [hakaton yolka 2026](https://github.com/Ruschywez/hakaton_yolka_2026.git)
- [jkh project](https://github.com/Ruschywez/jkh_project.git)

Also I want to try some features:

- [ ] mail verification;
- [ ] logs;
- [ ] encrypt users' data.

## How is it gonna work?

- [ ] make "sessions" for users;
- [ ] give users a unique key for the "session";
- [ ] take the key from the user for each request;
- [ ] check the status of the session and user's rights;
- [ ] if the status and rights are correct, then continue.

## What will be here?
I don't want to create a too complicated system:

#### Database
- [ ] users
- [ ] sessions
- [ ] REALLY SECRET INFORMATION :3

#### Server
- [ ] CRUD
- [ ] Security

#### Client
- [ ] Authorization
- [ ] Way to add `REALLY SECRET INFORMATION`
- [ ] Way to get `REALLY SECRET INFORMATION`

#### Is there anything else?
Also I want to create all tables to database for first start of server.
I will use SQLite with peewee.


#### Stack

| feature | why is this there? |
| - | - |
| aiosqlite | SQLite driver |
| peewee  | My favorite ORM for python |
| types-peewee | Peewee types support for PyLance |
| peewee-aio | Async support for peewee |
| bcrypt | |
| cryptography | |
| fastAPI | Simple HTTP API |
| 
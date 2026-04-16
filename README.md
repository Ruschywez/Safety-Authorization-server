## Secure Authorization (server)
localization:
- [eng](/README.md)  
- [ru](/README.ru.md)  

[client](https://github.com/Ruschywez/secure-authorization-client.git)

It's a simple project for self-learning, created with the goal of learning "how to create a safe API".

When I was creating systems in the past, they were really simple and unsafe.

The main problem with my systems was trusting the client too much. Servers never checked users' rights and anyone could access any information from the backend, just by using simple HTTP requests with a different ID.

For example, my other projects that have this problem:

- [hakaton yolka 2026](https://github.com/Ruschywez/hakaton_yolka_2026.git)
- [jkh project](https://github.com/Ruschywez/jkh_project.git)

Also I want to try some features:

- [ ] mail verification;
- [ ] logs;
- [x] encrypt users' data.

## How is it gonna work?

- [x] make "sessions" for users;
- [x] give users a unique key for the "session";
- [x] take the key from the user for each request;
- [x] check the status of the session and user's rights;
- [x] if the status and rights are correct, then continue.

## What will be here?
I don't want to create a too complicated system:

#### Database
- [x] users
- [x] sessions
- [x] REALLY SECRET INFORMATION :3

#### Server
- [x] CRUD
- [x] Security

#### Is there anything else?
Also I want to create all tables to database for first start of server.
I will use SQLite with peewee.

## Stack

| feature | why is this there? |
| - | - |
| aiosqlite | SQLite driver |
| peewee  | My favorite ORM for python |
| types-peewee | Peewee types support for PyLance |
| peewee-aio | Async support for peewee |
| fastAPI | Simple HTTP API |
| uvicorn | Server |

#### Installation

1) clone repository
2) load libs from requirements.txt
3) launch `create_db.py`

#### Launch

```cmd
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Project structure
```
serve/
├── docs/
│   └── ...  
├── src/
│   ├── __init__.py
│   ├── const.py
│   ├── container.py  
│   ├── encryption.py  
│   ├── entities.py  
│   ├── exception.py  
│   ├── imageManager.py  
│   ├── models.py  
│   ├── repositories.py  
│   ├── routers.py  
│   ├── services.py  
│   └── validation.py      
├── create_db.py
├── main.py
├── README.md
└── requirements.txt
```
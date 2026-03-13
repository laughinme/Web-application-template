# Fullstack monolith application template

The app requires postgres and redis launched locally to start. I prefer keeping it all as docker containers.

You can start postgresql via docker command:
```
docker run -d --name template-pg \
-e POSTGRES_USER=postgres \
-e POSTGRES_PASSWORD=secret \
-e POSTGRES_DB=template-pg \
-p 5432:5432 \
-v template_pg_data:/var/lib/postgresql/data \
postgres:17
```

Redis can also be started the same way:

```docker run -d --name redis -p 6379:6379 redis:latest```

Next step in running preexisting migrations to create database tables and seed data in them. It can be done using alembic:

```alembic upgrade head```

After these steps you can run the app locally with uvicorn:

```uvicorn main:app --host 0.0.0.0 --port 8080 --log-level debug --reload```

## Notifications runtime

The notifications stack now consists of three processes:

1. `backend` API
2. `backend-worker` (ARQ worker, sends e-mail via Resend and Telegram via Bot API)
3. `telegram-bot` (separate service with `/start` deeplink linking flow)

Docker Compose starts all of them:

```bash
make up
```

Manual local run:

```bash
# backend API
cd backend
PYTHONPATH=src poetry run uvicorn main:app --host 0.0.0.0 --port 8080 --reload

# notifications worker (separate terminal)
cd backend
PYTHONPATH=src poetry run arq workers.notifications_worker.WorkerSettings

# telegram bot (separate terminal)
cd bot
PYTHONPATH=src poetry run python -m telegram_bot.main
```

---

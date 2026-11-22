# RecoveryBot

A private Telegram companion and Android heartbeat agent for documenting an authorized app-recovery process.

## Safety scope
- The bot accepts non-sensitive progress notes only.
- It does not collect passwords, generate guesses, automate login attempts, or bypass authentication.
- The Android agent sends a periodic device/runtime heartbeat only.
- Do not upload account credentials, private keys, or personal app data to this repository.

## Railway layout
Deploy this repository directory as two Railway services from the same GitHub repository:
1. API service: start command `uvicorn server:app --host 0.0.0.0 --port $PORT`
2. Worker service: start command `python bot.py`

Set these variables on both services:
- `DATABASE_PATH=/data/recoverybot.sqlite3`
- `AGENT_SHARED_SECRET` (same long random value on API and worker)

Set these additional variables on the worker:
- `BOT_TOKEN` (from @BotFather)
- `ADMIN_TELEGRAM_ID` (your numeric Telegram user ID)

Attach a Railway Volume mounted at `/data` to the API and worker if they must share persistent SQLite data. For production, a managed PostgreSQL database is preferable to sharing SQLite between two services.

## Android agent
The agent uses only Python standard-library modules. Set:
- `RECOVERYBOT_API=https://YOUR-API-DOMAIN`
- `AGENT_SHARED_SECRET=the_same_secret_as_Railway`
- `DEVICE_ID=huawei-android`

Then run `python phone_agent.py`. Termius is an SSH client, not a local Python runtime; use a compatible Android Python environment to run this file on the handset.

## Telegram commands
- `/start`
- `/help`
- `/status`
- `/note <non-sensitive progress note>`
- `/history`

Never send passwords or one-time codes to the bot.

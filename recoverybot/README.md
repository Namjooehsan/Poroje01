# RecoveryBot

A private Telegram companion and Android heartbeat agent for documenting an authorized app-recovery process.

## Safety scope
- The bot accepts non-sensitive progress notes only.
- It does not collect passwords, generate guesses, automate login attempts, or bypass authentication.
- The Android agent sends a periodic device/runtime heartbeat only.
- Do not upload account credentials, private keys, or personal app data to this repository.

## Railway deployment (single service)
Deploy the repository with the Railway service root directory set to `recoverybot`.
The single web service runs both the FastAPI heartbeat API and Telegram polling bot in one process, sharing one SQLite database.

Start command:
`uvicorn server:app --host 0.0.0.0 --port $PORT`

Set these Railway variables:
- `BOT_TOKEN` (from @BotFather)
- `ADMIN_TELEGRAM_ID` (your numeric Telegram user ID)
- `AGENT_SHARED_SECRET` (a long random secret shared with the phone agent)
- `DATABASE_PATH=/data/recoverybot.sqlite3`

Attach a Railway Volume mounted at `/data` if you need the SQLite notes and device status to persist across redeploys. Without a volume, local database contents may be lost on redeploy.

## Android agent
The agent uses only Python standard-library modules. Set:
- `RECOVERYBOT_API=https://YOUR-RAILWAY-DOMAIN`
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

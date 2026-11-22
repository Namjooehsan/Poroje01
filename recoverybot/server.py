import hmac
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field
from database import init_db, update_device, get_device
from bot import build_application

telegram_app = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global telegram_app
    init_db()
    telegram_app = build_application()
    await telegram_app.initialize()
    await telegram_app.start()
    await telegram_app.updater.start_polling()
    yield
    await telegram_app.updater.stop()
    await telegram_app.stop()
    await telegram_app.shutdown()


app = FastAPI(title="RecoveryBot API", version="1.0.0", lifespan=lifespan)


class Heartbeat(BaseModel):
    device_id: str = Field(min_length=1, max_length=80)
    android_version: str = Field(default="unknown", max_length=40)
    python_version: str = Field(default="unknown", max_length=40)
    adb_status: str = Field(default="not_checked", max_length=40)


def authorize(value: str | None):
    expected = os.getenv("AGENT_SHARED_SECRET", "")
    if not expected or not value or not hmac.compare_digest(value, expected):
        raise HTTPException(status_code=401, detail="Unauthorized")


@app.get("/healthz")
def health():
    return {"ok": True, "service": "RecoveryBot API and Telegram bot"}


@app.post("/v1/agent/heartbeat")
def heartbeat(payload: Heartbeat, authorization: str | None = Header(default=None)):
    authorize(authorization)
    update_device(
        payload.device_id,
        payload.android_version,
        payload.python_version,
        payload.adb_status,
    )
    return {"accepted": True}


@app.get("/v1/device/{device_id}")
def device_status(device_id: str, authorization: str | None = Header(default=None)):
    authorize(authorization)
    row = get_device(device_id)
    if row is None:
        return {"online": False, "message": "No heartbeat received yet"}
    return {
        "online": True,
        "device_id": row["device_id"],
        "android_version": row["android_version"],
        "python_version": row["python_version"],
        "adb_status": row["adb_status"],
        "last_seen": row["last_seen"],
    }

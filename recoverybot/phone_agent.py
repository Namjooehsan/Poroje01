"""Minimal Android-side heartbeat agent. Python standard library only.

This agent reports device/runtime information to RecoveryBot. It does not
read, submit, guess, or store passwords and does not control login screens.
"""
import json
import os
import platform
import time
import urllib.request
import urllib.error

API_BASE = os.getenv("RECOVERYBOT_API", "").rstrip("/")
AGENT_SECRET = os.getenv("AGENT_SHARED_SECRET", "")
DEVICE_ID = os.getenv("DEVICE_ID", "huawei-android")


def post_heartbeat():
    if not API_BASE or not AGENT_SECRET:
        raise RuntimeError("Set RECOVERYBOT_API and AGENT_SHARED_SECRET.")
    payload = {
        "device_id": DEVICE_ID,
        "android_version": platform.release(),
        "python_version": platform.python_version(),
        "adb_status": "not_checked",
    }
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        API_BASE + "/v1/agent/heartbeat",
        data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": AGENT_SECRET,
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        return response.read().decode("utf-8")


def main():
    print("RecoveryBot phone agent started. Ctrl+C to stop.")
    while True:
        try:
            print(post_heartbeat())
        except (urllib.error.URLError, TimeoutError, RuntimeError) as exc:
            print("Connection error:", exc)
        time.sleep(60)


if __name__ == "__main__":
    main()

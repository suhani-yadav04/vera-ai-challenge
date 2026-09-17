from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from datetime import datetime, timezone
from services.llm import generate_message

from services.data_loader import load_all_data
from store import (
    contexts,
    versions,
    conversations
)
from services.message_builder import build_message

app = FastAPI()

seed_data = load_all_data()

import time

START_TIME = time.time()

@app.get("/v1/healthz")
def health():

    return {
        "status": "ok",
        "uptime_seconds": int(
            time.time() - START_TIME
        ),
        "contexts_loaded": {
            "category": len(contexts["category"]),
            "merchant": len(contexts["merchant"]),
            "customer": len(contexts["customer"]),
            "trigger": len(contexts["trigger"])
        }
    }



@app.get("/v1/metadata")
def metadata():

    return {
        "team_name": "Suhani Yadav",
        "team_members": [
            "Suhani Yadav"
        ],
        "model": "Groq Llama 3.3 70B + Rule Fallback",
        "approach": "AI-first contextual message generation with rule-based fallback",
        "contact_email": "Suhaniyadav1802@gmail.com",
        "version": "1.0",
        "submitted_at": datetime.now(
            timezone.utc
        ).isoformat()
    }


@app.post("/v1/context")
def context(payload: dict):

    scope = payload.get("scope")
    context_id = payload.get("context_id")
    version = payload.get("version", 1)

    if scope not in contexts:

        return {
            "accepted": False,
            "reason": "invalid_scope"
        }

    current_version = versions.get(
        context_id,
        0
    )

    if version <= current_version:

        return {
            "accepted": False,
            "reason": "stale_version",
            "current_version": current_version
        }

    contexts[scope][context_id] = payload.get(
        "payload",
        {}
    )

    versions[context_id] = version

    return {
    "accepted": True,
    "ack_id": f"ack_{context_id}_v{version}",
    "stored_at": datetime.now(
        timezone.utc
    ).isoformat()
}


@app.post("/v1/tick")
def tick(payload: dict):

    actions = []

    trigger_ids = payload.get(
        "available_triggers",
        []
    )

    for trigger_item in trigger_ids:
        if isinstance(trigger_item, dict):
            trigger_id = trigger_item.get("trigger_id")
        else:
            trigger_id = trigger_item

        if not trigger_id:
            continue

        trigger = contexts["trigger"].get(trigger_id)

        if not trigger:
            continue

        merchant_id = trigger.get("merchant_id")
        merchant = contexts["merchant"].get(merchant_id)

        if not merchant:
            for candidate in seed_data["merchants"]["merchants"]:
                if candidate.get("merchant_id") == merchant_id:
                    merchant = candidate
                    break

        if not merchant:
            continue

        message = build_message(
            merchant,
            trigger
        )

        actions.append(
            {
                "conversation_id":
                f"conv_{trigger_id}",

                "merchant_id":
                merchant_id,

                "customer_id":
                trigger.get(
                    "customer_id"
                ),

                "send_as":
                "vera",

                "trigger_id":
                trigger_id,

                "template_name":
                "vera_ai",

                "template_params":
                [],

                "body":
                message,

                "cta":
                "open_ended",

                "suppression_key":
                trigger.get(
                    "suppression_key",
                    ""
                ),

                "rationale":
                "Generated using category, merchant, trigger and customer context"
            }
        )

    return {
        "actions": actions
    }

@app.get("/v1/debug")
def debug():

    return {
        "merchant_keys": list(seed_data["merchants"].keys()),
        "customer_keys": list(seed_data["customers"].keys()),
        "trigger_keys": list(seed_data["triggers"].keys())
    }


@app.get("/v1/sample")
def sample():
    return seed_data["merchants"]


@app.get("/v1/check")
def check():
    return contexts["merchant"]



@app.get("/v1/merchant/{idx}")
def merchant(idx: int):
    return seed_data["merchants"]["merchants"][idx]



@app.get("/v1/simulate/{idx}")
def simulate(idx: int):

    merchant = seed_data["merchants"]["merchants"][idx]

    message = build_message(
        merchant,
        {}
    )

    return {
        "merchant": merchant["identity"]["name"],
        "message": message
    }



@app.get("/v1/all_merchants")
def all_merchants():
    return {
        "count": len(seed_data["merchants"]["merchants"]),
        "ids": [
            m["merchant_id"]
            for m in seed_data["merchants"]["merchants"]
        ]
    }

@app.post("/v1/reply")
def reply(payload: dict):

    message = payload.get(
        "message",
        ""
    ).lower()

    try:

        reply_prompt = f"""
Merchant replied:

{message}

Decide the next action.

Possible actions:

send
wait
end

Rules:

- If merchant accepted, return send
- If merchant declined, return end
- If merchant is unclear, return wait

Return only one word.
"""

        decision = generate_message(
            reply_prompt
        ).strip().lower()

        if "send" in decision:

            return {
                "action": "send",
                "body": "Great. I'll prepare the recommendation using your business data and recent performance trends.",
                "cta": "open_ended",
                "rationale": "AI detected positive intent"
            }

        if "wait" in decision:

            return {
                "action": "wait",
                "wait_seconds": 1800,
                "rationale": "AI requested wait"
            }

        if "end" in decision:

            return {
                "action": "end",
                "rationale": "AI detected decline intent"
            }

    except Exception as e:

        print("REPLY AI ERROR:", e)

    return {
        "action": "wait",
        "wait_seconds": 1800,
        "rationale": "Fallback wait"
    }

@app.post("/v1/teardown")
def teardown():

    contexts["category"].clear()
    contexts["merchant"].clear()
    contexts["customer"].clear()
    contexts["trigger"].clear()

    versions.clear()
    conversations.clear()

    return {
        "success": True
    }


@app.get("/")
def home():
    return {
        "service": "Magicpin Vera AI Challenge Bot",
        "status": "running",
        "team": "Suhani Yadav",
        "version": "1.0",
        "docs": "/docs",
        "health": "/v1/healthz",
        "metadata": "/v1/metadata"    }

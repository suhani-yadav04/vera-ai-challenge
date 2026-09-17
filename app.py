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


@app.get("/", response_class=HTMLResponse)
def home():
    return """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Vera AI | Magicpin</title>

<style>
* {
    box-sizing: border-box;
}

body {
    margin: 0;
    min-height: 100vh;
    background: #0b0b0b;
    color: #bdbdbd;
    font-family: "Courier New", monospace;
    overflow: hidden;
}

/* Background grid */
body::before {
    content: "";
    position: fixed;
    inset: 0;
    background:
        linear-gradient(#202020 1px, transparent 1px),
        linear-gradient(90deg, #202020 1px, transparent 1px);
    background-size: 80px 80px;
    opacity: 0.7;
}

.container {
    position: relative;
    z-index: 2;
    min-height: 100vh;
    padding: 55px 60px;
}

/* Vera logo */
.logo-box {
    width: 460px;
    border: 1px solid #555;
    padding: 30px;
    margin-top: 180px;
}

.logo {
    font-size: 52px;
    font-weight: bold;
    letter-spacing: 5px;
    color: #c0c0c0;
}

.magicpin {
    margin-top: 12px;
    font-size: 30px;
    letter-spacing: 3px;
}

/* Status text */
.status {
    margin-top: 35px;
    font-size: 14px;
    line-height: 2.4;
    letter-spacing: 1px;
}

.status .active {
    color: #eeeeee;
}

.cursor {
    display: inline-block;
    width: 8px;
    height: 15px;
    background: #aaa;
    margin-left: 5px;
    animation: blink 1s infinite;
}

@keyframes blink {
    50% {
        opacity: 0;
    }
}

/* Right-side blocks */
.visual {
    position: absolute;
    right: 7%;
    top: 18%;
    width: 420px;
    height: 430px;
}

.grid-box {
    position: absolute;
    width: 80px;
    height: 80px;
    border: 1px solid #333;
}

.g1 { left: 0; top: 0; }
.g2 { left: 80px; top: 0; }
.g3 { left: 160px; top: 0; }

.g4 { left: 80px; top: 80px; }
.g5 { left: 240px; top: 80px; }

.g6 { left: 160px; top: 160px; }
.g7 { left: 320px; top: 160px; }

.g8 { left: 0; top: 240px; }
.g9 { left: 80px; top: 240px; }

.pixel {
    position: absolute;
    width: 16px;
    height: 16px;
    background: #8b00ff;
    animation: float 2.5s infinite ease-in-out;
}

.green {
    background: #00f0ad;
}

@keyframes float {
    0%, 100% {
        transform: translateY(0);
        opacity: 0.75;
    }
    50% {
        transform: translateY(10px);
        opacity: 1;
    }
}

.p1 { left: 250px; top: 25px; }
.p2 { left: 266px; top: 41px; animation-delay: .3s; }
.p3 { left: 282px; top: 25px; animation-delay: .6s; }
.p4 { left: 250px; top: 57px; animation-delay: .9s; }

.p5 { left: 190px; top: 110px; animation-delay: .2s; }
.p6 { left: 206px; top: 126px; animation-delay: .5s; }

.p7 { left: 350px; top: 190px; animation-delay: .4s; }
.p8 { left: 366px; top: 206px; animation-delay: .8s; }

.p9 { left: 90px; top: 270px; animation-delay: .7s; }

.footer {
    position: absolute;
    bottom: 30px;
    left: 60px;
    font-size: 12px;
    color: #555;
    letter-spacing: 1px;
}

@media (max-width: 850px) {
    .container {
        padding: 30px;
    }

    .logo-box {
        width: 90%;
        margin-top: 150px;
    }

    .logo {
        font-size: 38px;
    }

    .magicpin {
        font-size: 23px;
    }

    .visual {
        opacity: 0.25;
        right: -100px;
    }

    .footer {
        left: 30px;
    }
}
</style>
</head>

<body>

<div class="container">

    <div class="logo-box">
        <div class="logo">VERA AI</div>
        <div class="magicpin">BY MAGICPIN</div>
    </div>

    <div class="status">
        02:53:06 <span class="active">INCOMING HTTP REQUEST DETECTED ...</span><br>
        02:53:09 <span class="active">SERVICE WAKING UP ...</span><br>
        02:53:13 <span class="active">ALLOCATING COMPUTE RESOURCES ...</span><br>
        02:53:16 <span class="active">PREPARING INSTANCE FOR INITIALIZATION ...</span><br>
        02:53:20 <span class="active">STARTING VERA AI INSTANCE ...</span><span class="cursor"></span>
    </div>

    <div class="visual">

        <div class="grid-box g1"></div>
        <div class="grid-box g2"></div>
        <div class="grid-box g3"></div>
        <div class="grid-box g4"></div>
        <div class="grid-box g5"></div>
        <div class="grid-box g6"></div>
        <div class="grid-box g7"></div>
        <div class="grid-box g8"></div>
        <div class="grid-box g9"></div>

        <div class="pixel p1"></div>
        <div class="pixel p2"></div>
        <div class="pixel p3"></div>
        <div class="pixel p4"></div>
        <div class="pixel green p5"></div>
        <div class="pixel p6"></div>
        <div class="pixel green p7"></div>
        <div class="pixel p8"></div>
        <div class="pixel green p9"></div>

    </div>

    <div class="footer">
        VERA AI · MAGICPIN · MERCHANT INTELLIGENCE SYSTEM · ONLINE
    </div>

</div>

</body>
</html>
"""

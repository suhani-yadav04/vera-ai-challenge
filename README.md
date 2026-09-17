# Vera AI Challenge Bot - https://vera-ai-challenge-tuwh.onrender.com

## Overview

This project is an AI-first merchant engagement bot built for the Magicpin Vera AI Challenge.

The bot receives contextual business data across four dimensions:

* Category Context
* Merchant Context
* Customer Context
* Trigger Context

Using these contexts, the system proactively generates personalized growth recommendations for merchants and handles conversational replies in real time.

The architecture combines:

* Groq Llama 3.3 70B for intelligent message generation
* Rule-based fallback engine for reliability
* Stateful context storage
* Conversation memory
* Version-controlled context updates

This ensures the bot remains operational even if the LLM becomes unavailable.

---

# Problem Statement

Local businesses receive large amounts of performance, customer, and category data.

Most merchants do not have the time to analyze:

* Customer retention issues
* Performance decline
* Subscription renewals
* Active offers
* Re-engagement opportunities
* Seasonal growth opportunities

The goal of Vera AI is to transform business data into proactive and actionable recommendations.

---

# System Architecture

## AI First

The primary recommendation engine uses:

* Groq API
* Llama 3.3 70B Versatile

The LLM receives:

* Category Context
* Merchant Context
* Trigger Context
* Customer Context

and generates personalized business recommendations.

---

## Rule-Based Fallback

If:

* Groq API fails
* Rate limits occur
* Network issues occur
* Invalid AI responses are generated

the system automatically falls back to a deterministic rule engine.

This guarantees uninterrupted operation.

Architecture:

AI Generation
↓
Success → Return AI Message

Failure
↓
Rule Engine
↓
Return Fallback Message

---

# Context Framework

The system stores all challenge contexts in memory.

```python
contexts = {
    "category": {},
    "merchant": {},
    "customer": {},
    "trigger": {}
}
```

Each context is stored independently and retrieved when needed.

---

## Category Context

Stores:

* Industry information
* Peer benchmarks
* Research digests
* Trend signals
* Offer catalogs
* Voice guidelines

Example:

* Dentist industry
* Average CTR
* Seasonal demand
* Research findings

---

## Merchant Context

Stores:

* Business identity
* Subscription details
* Performance metrics
* Offers
* Signals
* Historical conversations

Example:

* CTR
* Views
* Calls
* Subscription expiry
* Active promotions

---

## Customer Context

Stores:

* Customer relationship history
* Visit count
* Services received
* Preferences
* Current lifecycle state

Example:

* Lapsed customer
* Recall due
* Preferred communication channel

---

## Trigger Context

Stores actionable events.

Examples:

* Renewal due
* Recall reminder
* Research digest
* Performance decline
* Customer re-engagement

Triggers activate message generation.

---

# Version-Controlled Context Updates

The challenge requires idempotent context storage.

Each context update contains:

```json
{
  "context_id": "m1",
  "version": 2
}
```

The system rejects stale updates:

```json
{
  "accepted": false,
  "reason": "stale_version"
}
```

This prevents older data from overwriting newer information.

---

# Message Generation Pipeline

Step 1:

Judge activates trigger.

Step 2:

Bot retrieves:

* Merchant
* Category
* Customer
* Trigger

contexts.

Step 3:

Recommended action is determined.

Examples:

* Renewal
* Offer
* Winback
* Growth
* Content improvement

Step 4:

Prompt is built.

Step 5:

Groq LLM generates recommendation.

Step 6:

If AI fails:

Rule Engine generates recommendation.

---

# Prompt Engineering Strategy

The prompt prioritizes:

1. Active offers
2. Lapsed customers
3. Subscription expiry
4. Performance decline
5. Previous conversation history

The model is instructed to:

* Mention exact metrics
* Avoid hallucinations
* Recommend specific actions
* Sound like a business account manager
* End with a clear CTA

Example output:

"Meera, your CTR is below peer clinics and your Dental Cleaning offer is active. 124 high-risk customers are eligible for outreach. Would you like campaign drafts to improve engagement?"

---

# Conversation Management

The system maintains conversation state:

```python
conversations = {}
```

Conversation history is tracked using:

```json
{
  "conversation_id": "conv_001"
}
```

This enables multi-turn interactions.

---

# AI-Powered Reply Handling

When a merchant replies:

Example:

"yes send it"

The reply is classified by the LLM.

Possible actions:

* send
* wait
* end

AI Classification:

Merchant Reply
↓
Groq LLM
↓
send / wait / end

---

## Fallback Reply Handling

If the AI fails:

Keyword-based rules handle:

Positive Intent

* yes
* okay
* send
* haan

Negative Intent

* stop
* spam
* not interested

Auto Replies

* thank you for contacting
* business account
* we will respond shortly

---

# Challenge Endpoints

## GET /v1/healthz

Returns:

* System health
* Uptime
* Loaded contexts

---

## GET /v1/metadata

Returns:

* Team information
* Model details
* Submission metadata

---

## POST /v1/context

Stores:

* Category
* Merchant
* Customer
* Trigger

contexts.

Supports versioning.

---

## POST /v1/tick

Receives active triggers.

Generates proactive actions.

Returns:

```json
{
  "actions": [...]
}
```

---

## POST /v1/reply

Processes merchant replies.

Returns:

```json
{
  "action": "send"
}
```

or

```json
{
  "action": "wait"
}
```

or

```json
{
  "action": "end"
}
```

---

## POST /v1/teardown

Clears:

* Context store
* Versions
* Conversations

Used after evaluation ends.

---

# State Management

Stored in memory:

```python
contexts
versions
conversations
```

This satisfies challenge requirements while keeping implementation lightweight.

---

# Reliability Features

* AI-first architecture
* Rule-based fallback
* Auto-reply detection
* Context versioning
* Stateful memory
* Trigger-based activation
* Customer-aware recommendations
* Graceful conversation termination

---

# Technology Stack

Backend

* FastAPI

LLM

* Groq API
* Llama 3.3 70B Versatile

Environment Management

* Python Dotenv

Language

* Python 3.x

---

# Project Structure

```text
vera-ai/

├── app.py
├── store.py
├── requirements.txt
├── README.md
├── .env
├── .gitignore

├── services/
│   ├── data_loader.py
│   ├── decision.py
│   ├── llm.py
│   ├── prompt_builder.py
│   └── message_builder.py

├── data/
│   ├── merchants_seed.json
│   ├── customers_seed.json
│   └── triggers_seed.json
```

---

# Run Locally

Install dependencies:

```bash
pip install -r requirements.txt
```

Create:

```env
GROQ_API_KEY=your_api_key
```

Run:

```bash
uvicorn app:app --reload
```

Open:

```text
 http://127.0.0.1:8000
```

for Swagger UI.

---

# Author
 Suhani Yadav

Built for the Magicpin Vera AI Challenge.

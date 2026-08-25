# BE-A9-Background-Job-API

A small FastAPI service that moves a slow AI report-generation call out of the request cycle and into an Inngest background job. The endpoint answers instantly with `202`, a background function does the slow work, a status endpoint reports progress, and a cron job runs independently on a schedule.

## What this is

- `POST /reports` — accepts a report request, returns `202` immediately with an `id`
- `GET /reports/{id}` — polls the status of a report: `pending` → `done` (or `failed`)
- Background function `make-report` — does the slow work (the A6 AI call), with retries
- Cron function `heartbeat` — runs every minute, logs a summary of report statuses
- Everything is orchestrated by [Inngest](https://www.inngest.com/), run locally via the Inngest Dev Server

## How to run

Two terminals, two commands.

**Terminal 1 — the API**
```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

**Terminal 2 — the Inngest Dev Server**
```bash
npx inngest-cli@latest dev -u http://localhost:8000/api/inngest
```

Dashboard: http://localhost:8288

## Endpoints & functions

| Type | Name | Trigger | Purpose |
|---|---|---|---|
| Endpoint | `GET /health` | HTTP request | Liveness check |
| Endpoint | `POST /reports` | HTTP request | Accepts a report request, returns `202` + `id` instantly |
| Endpoint | `GET /reports/{id}` | HTTP request | Returns report status: `pending`, `done`, or `failed`; `404` if unknown |
| Function | `say-hello` | Event `test/hello` | Stage 1 sanity check function |
| Function | `make-report` | Event `report/requested` | Background job — runs the slow AI call, saves the result, retries on failure |
| Function | `heartbeat` | Cron `* * * * *` | Runs every minute, logs counts of pending/done/failed reports |

## Proof — 202 then poll

```
$ time curl -i -X POST http://localhost:8000/reports -H "Content-Type: application/json" -d '{"topic":"cats"}'
HTTP/1.1 202 Accepted
{"id":"3f9a...","status":"pending"}
real    0m0.041s

$ curl http://localhost:8000/reports/3f9a...
{"id":"3f9a...","topic":"cats","status":"pending"}

# ~10 seconds later
$ curl http://localhost:8000/reports/3f9a...
{"id":"3f9a...","topic":"cats","status":"done","result":"..."}
```

## Stage 3 — retries vs. validation

Missing input is rejected at the door (`400`, no job ever created); a failure at a valid moment gets a retry. Validation catches wrong data, retries catch wrong timing — a `POST` with no `topic` never reaches Inngest, but a `topic` of `"fail"` is accepted and retried 3 times before the run ends `Failed`.

## Stage 4 — cron expressions

- Every day at 08:00 → `0 8 * * *`
- Every Sunday at 22:00 → `0 22 * * 0`

(Built and verified on [crontab.guru](https://crontab.guru).)

## Dashboard screenshot

_![Inngest dashboard showing make-report, a failed retry run, and heartbeat cron runs](./docs/dashboard.png)_

## AI vs me (bonus stage)

**Prompt used:**
> _(paste your own from-memory prompt here — do not copy this assignment doc)_

**What the AI did better:**
- _TBD_

**What it got wrong or silently ignored:**
- _TBD_

**What my prompt forgot to specify (and what the AI decided for me):**
- _TBD_

**After one rematch (improved prompt):**
- _TBD_

AI-generated code lives in `ai-version/` and was never merged into the hand-built submission.
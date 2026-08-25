import uuid
from typing import Any

import inngest  # type: ignore[import-not-found]
from fastapi import FastAPI, HTTPException  # type: ignore[import-not-found]
from pydantic import BaseModel  # type: ignore[import-not-found]

app = FastAPI()
reports: dict[str, dict[str, Any]] = {}

inngest_client = inngest.Inngest(app_id="background-job-api")


class ReportRequest(BaseModel):
    topic: str


@app.post("/reports", status_code=202)
async def create_report(req: ReportRequest):
    if not req.topic:
        raise HTTPException(status_code=400, detail="topic is required")

    report_id = str(uuid.uuid4())
    reports[report_id] = {"id": report_id, "topic": req.topic, "status": "pending"}

    await inngest_client.send(
        inngest.Event(name="report/requested", data={"id": report_id, "topic": req.topic})
    )
    return {"id": report_id, "status": "pending"}


@app.get("/reports/{report_id}")
def get_report(report_id: str):
    report = reports.get(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="not found")
    return report


@inngest_client.create_function(
    fn_id="make-report",
    trigger=inngest.TriggerEvent(event="report/requested"),
)
async def make_report(ctx: inngest.Context, step: inngest.Step) -> None:
    report_id = ctx.event.data["id"]
    topic = ctx.event.data["topic"]

    async def build() -> None:
        result = f"Generated report for: {topic}"
        reports[report_id]["status"] = "done"
        reports[report_id]["result"] = result

    await step.run("build-report", build)


inngest.fast_api.serve(app, inngest_client, [make_report])
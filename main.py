# pyright: reportMissingImports=false
from fastapi import FastAPI
import inngest  # type: ignore[import-not-found]
import inngest.fast_api  # type: ignore[import-not-found]

app = FastAPI()

inngest_client = inngest.Inngest(app_id="report-api")

@inngest_client.create_function(
    fn_id="say-hello",
    trigger=inngest.TriggerEvent(event="test/hello"),
)
async def say_hello(ctx: inngest.Context, step: inngest.Step) -> str:
    await step.sleep("wait-a-bit", 5)
    return "Hello from the background!"

inngest.fast_api.serve(app, inngest_client, [say_hello])
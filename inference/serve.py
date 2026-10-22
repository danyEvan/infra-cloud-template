# serve.py: minimal CPU inference server with health check and Prometheus metrics
import os
import time

from fastapi import FastAPI, Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from pydantic import BaseModel
from transformers import pipeline

MODEL_ID = os.environ.get("MODEL_ID", "distilgpt2")
generator = pipeline("text-generation", model=MODEL_ID)  # weights go to HF_HOME

app = FastAPI()
REQUESTS = Counter("inferencia_requests_total", "Inference requests served")
LATENCY = Histogram("inferencia_latency_seconds", "Inference latency in seconds")


class Prompt(BaseModel):
    prompt: str
    max_new_tokens: int = 30


@app.post("/predict")
def predict(body: Prompt) -> dict:
    start = time.perf_counter()
    out = generator(body.prompt, max_new_tokens=body.max_new_tokens)[0]["generated_text"]
    LATENCY.observe(time.perf_counter() - start)
    REQUESTS.inc()
    return {"model": MODEL_ID, "output": out}


@app.get("/healthz")
def healthz() -> dict:
    return {"status": "ok"}


@app.get("/metrics")
def metrics() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import json, numpy as np
from pathlib import Path

app = FastAPI()

DATA_PATH = Path(__file__).parent / "telemetry.json"
with open(DATA_PATH) as f:
    TELEMETRY = json.load(f)

@app.options("/")
async def options():
    return JSONResponse({}, headers={
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
    })

@app.post("/")
async def analytics(request: Request):
    body = await request.json()
    regions = body.get("regions", [])
    threshold_ms = body.get("threshold_ms", 180)
    result = {}
    for region in regions:
        records = [r for r in TELEMETRY if r["region"] == region]
        latencies = [r["latency_ms"] for r in records]
        uptimes = [r["uptime_pct"] for r in records]
        result[region] = {
            "avg_latency": round(float(np.mean(latencies)), 4),
            "p95_latency": round(float(np.percentile(latencies, 95)), 4),
            "avg_uptime": round(float(np.mean(uptimes)), 4),
            "breaches": int(sum(1 for l in latencies if l > threshold_ms))
        }
    return JSONResponse(content=result, headers={
        "Access-Control-Allow-Origin": "*"
    })

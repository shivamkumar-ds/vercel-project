from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import json, numpy as np
from pathlib import Path

app = FASTAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

#load telemetry data
DATA_PATH = Path(__file__).parent / "data" / "telemetry.json"
with open(DATA_PATH) as f:
    TELEMETRY = json.load(f)

@app.post("/")
async def handle_post(request: Request):
    body = await request.json()
    regions = body.get("regions",[])
    threshold = body.get("threshold",0)

    results = {}
    for region in regions:
        records = TELEMETRY.get(region, [])
        latencies = [rec["latency"] for rec in records]
        uptimes = [rec["uptime"] for rec in records]

        results[region] = {
            "average_latency": round(np.mean(latencies),4) if latencies else None,
            "average_uptime": round(np.mean(uptimes),4) if uptimes else None,
            "p95_latency": round(np.percentile(latencies, 95),4) if latencies else None,
            "breaches": int(sum(1 for lat in latencies if lat > threshold)) if latencies else None
        }

    return results

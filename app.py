# app.py - FastAPI application to serve MongoDB data as JSON

from fastapi import FastAPI
from fastapi.responses import JSONResponse, StreamingResponse
from pymongo import MongoClient
import json
from bson import json_util  # To handle BSON types like ObjectId
from typing import List, Dict

app = FastAPI(title="MongoDB Data Server")

# MongoDB connection (use environment variables in production for security)
MONGO_URI = "mongodb+srv://elvishyadav_opm:naman1811421@cluster0.uxuplor.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(MONGO_URI)
db = client["unacademy_db"]
educators_col = db["educators"]

def fetch_educators() -> List[Dict]:
    """
    Fetch all documents from the educators collection.
    """
    educators = list(educators_col.find({}))  # Fetch all documents
    # Convert BSON to JSON serializable format
    return json.loads(json_util.dumps(educators))

def stream_json(data: List[Dict]):
    """
    Generator to stream JSON data line by line (JSON Lines format for large data).
    """
    yield '[\n'
    for i, item in enumerate(data):
        yield json.dumps(item, default=json_util.default)
        if i < len(data) - 1:
            yield ',\n'
        else:
            yield '\n'
    yield ']\n'

@app.get("/data", response_model=List[Dict])
async def get_data():
    """
    Endpoint to get all educators data as streamed JSON.
    Use StreamingResponse for large datasets to avoid loading everything in memory at once.
    """
    data = fetch_educators()
    return StreamingResponse(stream_json(data), media_type="application/json")

# Run the app with: uvicorn app:app --reload

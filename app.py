from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pymongo import MongoClient
import json
from bson import json_util
from typing import List, Dict
import os

app = FastAPI(title="MongoDB Data Server")

# MongoDB connection (using environment variable for security)
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://elvishyadav_opm:naman1811421@cluster0.uxuplor.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
client = MongoClient(MONGO_URI)
db = client["unacademy_db"]
educators_col = db["educators"]

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

@app.get("/data")
async def get_all_data():
    """
    Endpoint to get all educators data as streamed JSON.
    """
    data = list(educators_col.find({}))
    return StreamingResponse(stream_json(data), media_type="application/json")

@app.get("/search_educator={keyword}")
async def search_educator(keyword: str):
    """
    Search educators by first_name or last_name containing the keyword (case-insensitive).
    Returns full educator data including courses and batches.
    """
    query = {
        "$or": [
            {"first_name": {"$regex": keyword, "$options": "i"}},
            {"last_name": {"$regex": keyword, "$options": "i"}}
        ]
    }
    data = list(educators_col.find(query))
    return StreamingResponse(stream_json(data), media_type="application/json")

@app.get("/search_batch={keyword}")
async def search_batch(keyword: str):
    """
    Search batches by name containing the keyword (case-insensitive).
    Returns batch data from all educators.
    """
    query = {
        "batches.name": {"$regex": keyword, "$options": "i"}
    }
    data = []
    for educator in educators_col.find(query, {"batches": 1}):
        for batch in educator.get("batches", []):
            if keyword.lower() in batch["name"].lower():
                data.append(batch)
    return StreamingResponse(stream_json(data), media_type="application/json")

@app.get("/search_courses={keyword}")
async def search_courses(keyword: str):
    """
    Search courses by name containing the keyword (case-insensitive).
    Returns course data from all educators.
    """
    query = {
        "courses.name": {"$regex": keyword, "$options": "i"}
    }
    data = []
    for educator in educators_col.find(query, {"courses": 1}):
        for course in educator.get("courses", []):
            if keyword.lower() in course["name"].lower():
                data.append(course)
    return StreamingResponse(stream_json(data), media_type="application/json")

# Run the app with: uvicorn app:app --reload

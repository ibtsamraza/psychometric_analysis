# main.py
import sys
import os
from fastapi import FastAPI, UploadFile, File, Form, Response
from agent import analyze_psychometric_scores
from utils import extract_score, extract_items, filter_subdomain, check_response_bias, check_social_desireablitiy
import pandas as pd
from typing import Dict, Any
from fastapi.middleware.cors import CORSMiddleware
import logging
from fastapi.responses import JSONResponse
from socket_manager import sio, socket_app
import time
import asyncio
from sse_starlette.sse import EventSourceResponse
from session_manager import update_session_status, session_status
import json

# Combine with your FastAPI app
app = FastAPI()
app.mount('/socket.io', socket_app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Temporarily allow all origins for testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# # Add a simple in-memory store for session status
# session_status = {}

# async def update_session_status(session_id, agent, status, progress):
#     """Update the status for a session"""
#     session_status[session_id] = {
#         'agent': agent,
#         'status': status,
#         'progress': progress,
#         'timestamp': time.time()
#     }
#     print(f"Updated status for {session_id}: {agent} - {status} - {progress}%")

@app.post("/analyze/")
async def analyze_psychometric(
    scores_file: UploadFile = File(...),
    items_file: UploadFile = File(...),
    session_id: str = Form(None)
) -> Dict[str, Any]:
    """
    Analyze psychometric scores and items from uploaded Excel files
    
    Args:
        scores_file: Excel file containing domain and subdomain scores
        items_file: Excel file containing item responses
        session_id: Unique identifier for the analysis session
        
    Returns:
        Dict containing analysis results and metadata
    """
    try:
        # If no session_id is provided, create one
        if not session_id:
            session_id = str(time.time())
            print(f"Created new session ID: {session_id}")
        else:
            print(f"Using provided session ID: {session_id}")
        
        # Initial progress update
        print(f"Sending initial progress update for session {session_id}")
        await sio.emit('agent_update', {
            'session_id': session_id,
            'agent': 'preprocessing',
            'status': 'Processing uploaded files...',
            'progress': 5
        })
        print("Initial progress update sent")
        
        # Check file extensions
        allowed_extensions = {'.xlsx', '.xls'}
        scores_ext = os.path.splitext(scores_file.filename)[1].lower()
        items_ext = os.path.splitext(items_file.filename)[1].lower()
        
        if scores_ext not in allowed_extensions:
            return {
                "error": f"Invalid scores file format. Expected Excel file (.xlsx, .xls), got {scores_ext}",
                "status": "failed"
            }
            
        if items_ext not in allowed_extensions:
            return {
                "error": f"Invalid items file format. Expected Excel file (.xlsx, .xls), got {items_ext}",
                "status": "failed"
            }
        
        logging.info("Received files for analysis")
        # Save uploaded files temporarily
        scores_path = "temp_scores.xlsx"
        items_path = "temp_items.xlsx"
        
        with open(scores_path, "wb") as f:
            f.write(await scores_file.read())
        
        with open(items_path, "wb") as f:
            f.write(await items_file.read())
        
        # Extract data from files
        scores_data = extract_score(scores_path)
        items_data, response_bias, high_response_bias = extract_items(items_path)
        
        
        # Process each sheet's data
        all_analyses = []
        for sheet_data in scores_data:

            sheet_items = next(
                (item for item in items_data if item["sheet_name"] == sheet_data["sheet_name"]),
                None
            )
            
            if not sheet_items:
                # Clean up temporary files
                os.remove(scores_path)
                os.remove(items_path)
                
                # Return error response
                return JSONResponse(
                    status_code=400,
                    content={
                        "error": f"No matching items data found for sheet '{sheet_data['sheet_name']}'.",
                        "status": "failed"
                    }
                )
            
            # Check for high bias levels
            if high_response_bias:
                all_analyses.append({
                    "sheet_name": sheet_data["sheet_name"],
                    "analysis":{"Psychometric Analysis": "The individual seems to have taken the test carefully, possibly to conceal certain aspects of themselves. The scores may not accurately reflect their traits and skills. Assessment during the interview is recommended.",
                                "Item Analysis" : ""
                                } ,
                })
                continue
            
            # Filter subdomains into strengths and development areas
            filtered_data, social_desirable, high_social_desireable = filter_subdomain(sheet_data["data"])
            
            # Check for high social desirability
            if high_social_desireable:
                all_analyses.append({
                    "sheet_name": sheet_data["sheet_name"],
                    "analysis": {"Psychometric Analysis": "According to the test scores, the candidate seems to have a tendency to appear in a desirable way. Due to this factor of social desirability, her test scores may not be interpreted as accurate presentation of her skills.",
                                 "Item Analysis" : ""   
                    },
                })
                continue
           
            # Prepare input for agent
            agent_input = {
                "scores": {
                    "strength": filtered_data["Strengths"],
                    "development_area": filtered_data["Development areas"]
                },
                "items": sheet_items,
                "metadata": {
                    "response_bias": response_bias,
                    "social_desirable": social_desirable
                }
            }
           
            # Get analysis from agent
            analysis = await analyze_psychometric_scores(agent_input, session_id)
            
            
            all_analyses.append({
                "sheet_name": sheet_data["sheet_name"],
                "analysis": analysis,
            })
        
        # Clean up temporary files
        os.remove(scores_path)
        os.remove(items_path)
        
        return {
            "analyses": all_analyses
        }
        logging.info("Files processed successfully")

        
    except Exception as e:
        logging.error(f"Error occurred: {e}")
        await sio.emit('agent_update', {
            'session_id': session_id,
            'agent': 'error',
            'status': f'Error: {str(e)}',
            'progress': 0
        })
        return {
            "error": str(e),
            "status": "failed"
        }

@app.get("/")
async def root():
    return {
        "message": "Psychometric Analysis API",
        "version": "1.0.0",
        "endpoints": {
            "/analyze/": "POST - Upload scores and items Excel files for analysis"
        }
    }

@app.get("/test-socket/{session_id}")
async def test_socket(session_id: str):
    """Test socket.io connection by sending a test event"""
    await sio.emit('agent_update', {
        'session_id': session_id,
        'agent': 'test',
        'status': 'This is a test message',
        'progress': 50
    })
    return {"message": f"Test event sent to session {session_id}"}

@app.get("/socket-debug")
async def socket_debug():
    """Get debug information about socket.io connections"""
    # Get information about active Socket.IO connections
    active_sids = list(sio.manager.get_rooms().get('', set()))
    
    return {
        "active_connections": len(active_sids),
        "connection_ids": active_sids,
        "rooms": sio.manager.get_rooms()
    }

@app.get("/test-progress/{session_id}")
async def test_progress(session_id: str):
    """Test progress updates by sending multiple events"""
    print(f"Starting test progress for session {session_id}")
    
    # Send updates using the session_status store
    await update_session_status(
        session_id,
        'test',
        'Starting test sequence...',
        0
    )
    
    # Send updates with delays
    for i in range(1, 11):
        await asyncio.sleep(1)  # Wait 1 second between updates
        progress = i * 10
        await update_session_status(
            session_id,
            'test',
            f'Test progress: {progress}%',
            progress
        )
        print(f"Updated status for test progress {i}/10 for session {session_id}")
    
    return {"message": f"Test progress sequence completed for session {session_id}"}

@app.get("/ping")
async def ping():
    """Simple endpoint to test connectivity"""
    return {"status": "ok", "timestamp": time.time()}

@app.get("/status/{session_id}")
async def get_status(session_id: str):
    """Get the current status for a session"""
    if session_id in session_status:
        return {
            "session_id": session_id,
            **session_status[session_id]
        }
    return {
        "session_id": session_id,
        "agent": "unknown",
        "status": "No status available",
        "progress": 0,
        "timestamp": time.time()
    }

@app.get("/events/{session_id}")
async def events(session_id: str, response: Response):
    """SSE endpoint for real-time updates"""
    print(f"SSE connection requested for session: {session_id}")
    
    # Set correct headers for SSE
    response.headers["Content-Type"] = "text/event-stream"
    response.headers["Cache-Control"] = "no-cache"
    response.headers["Connection"] = "keep-alive"
    response.headers["X-Accel-Buffering"] = "no"  # Important for Nginx
    
    async def event_generator():
        # Send initial event
        initial_status = session_status.get(session_id, {
            'agent': 'initializing',
            'status': 'Starting...',
            'progress': 0,
            'timestamp': time.time()
        })
        
        print(f"Sending initial SSE event for session {session_id}: {initial_status}")
        
        # Format the event properly with proper JSON serialization
        data = {
            "session_id": session_id,
            **initial_status
        }
        
        # Debug the JSON serialization
        json_data = json.dumps(data)
        print(f"Serialized JSON data: {json_data}")
        
        yield {
            "event": "update",
            "data": json_data
        }
        
        # Poll for updates
        last_update = initial_status.get('timestamp', 0)
        poll_count = 0
        while True:
            await asyncio.sleep(1)  # Check every second
            poll_count += 1
            
            if poll_count % 10 == 0:  # Log every 10 polls to avoid excessive logging
                print(f"Polling for updates for session {session_id} (poll #{poll_count})")
            
            current_status = session_status.get(session_id)
            if current_status and current_status.get('timestamp', 0) > last_update:
                last_update = current_status.get('timestamp', 0)
                print(f"Sending SSE update for session {session_id}: {current_status}")
                data = {
                    "session_id": session_id,
                    **current_status
                }
                json_data = json.dumps(data)
                print(f"Serialized JSON data: {json_data}")
                yield {
                    "event": "update",
                    "data": json_data
                }
            
            # Stop if we've reached 100% progress
            if current_status and current_status.get('progress', 0) >= 100:
                print(f"SSE stream completed for session {session_id} (reached 100%)")
                break
            
            # Limit the polling duration to avoid infinite loops
            if poll_count > 300:  # 5 minutes max
                print(f"SSE stream timeout for session {session_id} (max polls reached)")
                break
    
    return EventSourceResponse(event_generator())

@app.get("/simple-sse")
async def simple_sse(response: Response):
    """Simple SSE endpoint for testing"""
    response.headers["Content-Type"] = "text/event-stream"
    response.headers["Cache-Control"] = "no-cache"
    response.headers["Connection"] = "keep-alive"
    response.headers["X-Accel-Buffering"] = "no"
    
    async def event_generator():
        # Send a simple event
        yield {
            "event": "update",
            "data": json.dumps({"message": "Hello from SSE", "timestamp": time.time()})
        }
        
        # Send more events with delays
        for i in range(1, 6):
            await asyncio.sleep(1)
            yield {
                "event": "update",
                "data": json.dumps({"message": f"Event {i}", "timestamp": time.time()})
            }
    
    return EventSourceResponse(event_generator())

@app.get("/simulate-analysis/{session_id}")
async def simulate_analysis(session_id: str):
    """Simulate a full analysis with progress updates"""
    print(f"Starting simulated analysis for session {session_id}")
    
    # Initial update
    await update_session_status(
        session_id,
        'psychometric_analysis',
        'Starting analysis...',
        10
    )
    
    # Simulate the different stages of analysis
    stages = [
        ('psychometric_analysis', 'Analyzing psychometric data...', 20),
        ('psychometric_analysis', 'Processing initial results...', 30),
        ('check_missing', 'Checking for missing information...', 40),
        ('judge_analysis', 'Evaluating analysis quality...', 50),
        ('correlated_analysis', 'Analyzing correlated domains...', 60),
        ('check_bias', 'Checking for response bias...', 70),
        ('item_analysis', 'Performing item-level analysis...', 80),
        ('item_analysis', 'Finalizing analysis...', 90),
        ('complete', 'Analysis complete!', 100)
    ]
    
    for agent, status, progress in stages:
        await asyncio.sleep(2)  # Simulate processing time
        await update_session_status(session_id, agent, status, progress)
        print(f"Updated status: {agent} - {status} - {progress}%")
    
    return {"message": f"Simulated analysis completed for session {session_id}"}

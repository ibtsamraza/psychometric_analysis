# main.py
import os
import time
import json
import asyncio
import logging
from typing import Dict, Any

from fastapi import FastAPI, UploadFile, File, Form, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sse_starlette.sse import EventSourceResponse

from agent import analyze_psychometric_scores
from utils import extract_score, extract_items, filter_subdomain
from socket_manager import socket_app, sio
from session_manager import update_session_status, session_status

# Initialize FastAPI app and mount Socket.IO
app = FastAPI()
app.mount('/socket.io', socket_app)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # you can restrict this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/analyze/")
async def analyze_psychometric(
    scores_file: UploadFile = File(...),
    items_file: UploadFile = File(...),
    session_id: str = Form(None)
) -> Dict[str, Any]:
    """
    Analyze psychometric scores and items from uploaded Excel files
    """
    try:
        # Generate a new session_id if not provided
        if not session_id:
            session_id = str(time.time())
            logging.info(f"Created new session ID: {session_id}")
        else:
            logging.info(f"Using provided session ID: {session_id}")

        # Initial progress update
        # await update_session_status(
        #     session_id,
        #     agent='preprocessing',
        #     status='Processing uploaded files...',
        #     progress=5

        # )

        # Validate file extensions
        allowed_ext = {'.xlsx', '.xls'}
        s_ext = os.path.splitext(scores_file.filename)[1].lower()
        i_ext = os.path.splitext(items_file.filename)[1].lower()
        if s_ext not in allowed_ext:
            return JSONResponse(
                status_code=400,
                content={"error": f"Invalid scores file format: {s_ext}", "status": "failed"}
            )
        if i_ext not in allowed_ext:
            return JSONResponse(
                status_code=400,
                content={"error": f"Invalid items file format: {i_ext}", "status": "failed"}
            )

        # Save uploads
        scores_path = 'temp_scores.xlsx'
        items_path = 'temp_items.xlsx'
        with open(scores_path, 'wb') as f:
            f.write(await scores_file.read())
        with open(items_path, 'wb') as f:
            f.write(await items_file.read())

        # Extract data
        scores_data = extract_score(scores_path)
        items_data, response_bias, high_response_bias = extract_items(items_path)

        all_analyses = []
        # Iterate sheets and analyze
        for sheet in scores_data:
            match = next(
                (itm for itm in items_data if itm['sheet_name'] == sheet['sheet_name']),
                None
            )
            if not match:
                os.remove(scores_path)
                os.remove(items_path)
                return JSONResponse(
                    status_code=400,
                    content={
                        "error": f"No matching items for sheet '{sheet['sheet_name']}'",
                        "status": "failed"
                    }
                )

            # Check for high bias levels
            if high_response_bias:
                all_analyses.append({
                    "sheet_name": sheet["sheet_name"],
                    "analysis":{"Psychometric Analysis": "The individual seems to have taken the test carefully, possibly to conceal certain aspects of themselves. The scores may not accurately reflect their traits and skills. Assessment during the interview is recommended.",
                                "Item Analysis" : ""
                                } ,
                })
                continue
            
            # Filter subdomains into strengths and development areas
            filtered, social_desirable, high_social_desireable = filter_subdomain(sheet["data"])
            
            # Check for high social desirability
            if high_social_desireable:
                all_analyses.append({
                    "sheet_name": sheet["sheet_name"],
                    "analysis": {"Psychometric Analysis": "According to the test scores, the candidate seems to have a tendency to appear in a desirable way. Due to this factor of social desirability, her test scores may not be interpreted as accurate presentation of her skills.",
                                 "Item Analysis" : ""   
                    },
                })
                continue

            # Call agent for full analysis
            agent_input = {
                'scores': {
                    'strength': filtered['Strengths'],
                    'development_area': filtered['Development areas']
                },
                'items': match,
                'metadata': {
                    'response_bias': response_bias,
                    'social_desirable': social_desirable
                },
                'name': sheet['sheet_name'],
            }

            result = await analyze_psychometric_scores(agent_input, session_id)
            all_analyses.append({
                'sheet_name': sheet['sheet_name'],
                'analysis': result
            })

        # Cleanup
        os.remove(scores_path)
        os.remove(items_path)

        return {'analyses': all_analyses}

    except Exception as e:
        logging.exception('Error in /analyze/')
        await update_session_status(
            session_id,
            agent='error',
            status=str(e),
            progress=0,
            name='',
        )
        return JSONResponse(
            status_code=500,
            content={"error": str(e), "status": "failed"}
        )

# Health & utility endpoints
@app.get('/')
async def root():
    return {
        'message': 'Psychometric Analysis API',
        'version': '1.0.0'
    }

@app.get('/status/{session_id}')
async def get_status(session_id: str):
    info = session_status.get(session_id)
    if info:
        return {'session_id': session_id, **info}
    return {'session_id': session_id, 'status': 'unknown', 'progress': 0}

@app.get('/events/{session_id}')
async def sse_events(session_id: str, response: Response):
    # SSE setup
    response.headers.update({
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'X-Accel-Buffering': 'no'
    })
    async def generator():
        last_ts = 0
        while True:
            await asyncio.sleep(1)
            data = session_status.get(session_id)
            if not data:
                continue
            if data['timestamp'] > last_ts:
                last_ts = data['timestamp']
                event_data = {'session_id': session_id, **data}
                print(f"Sending SSE event: {event_data}")  # Debug log
                yield {'event': 'update', 'data': json.dumps(event_data)}
            if data.get('progress', 0) >= 100:
                break
    return EventSourceResponse(generator())

@app.get('/test-socket/{session_id}')
async def test_socket(session_id: str):
    await sio.emit('agent_update', {'session_id': session_id, 'agent': 'test', 'status': 'Hello', 'progress': 50})
    return {'message': f'Test event sent to {session_id}'}

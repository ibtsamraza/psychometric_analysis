# main.py
from fastapi import FastAPI, UploadFile, File
from agent import analyze_psychometric_scores
from utils import extract_score, extract_items, filter_subdomain, check_response_bias, check_social_desireablitiy
import pandas as pd
from typing import Dict, Any
from fastapi.middleware.cors import CORSMiddleware
import logging

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React's default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/analyze/")
async def analyze_psychometric(
    scores_file: UploadFile = File(...),
    items_file: UploadFile = File(...)
) -> Dict[str, Any]:
    """
    Analyze psychometric scores and items from uploaded Excel files
    
    Args:
        scores_file: Excel file containing domain and subdomain scores
        items_file: Excel file containing item responses
        
    Returns:
        Dict containing analysis results and metadata
    """
    try:
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
            # Find matching items data for this sheet
            sheet_items = next(
                (item["data"] for item in items_data if item["sheet_name"] == sheet_data["sheet_name"]),
                None
            )
            
            if not sheet_items:
                continue
            
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
            analysis = analyze_psychometric_scores(agent_input)
            
            
            all_analyses.append({
                "sheet_name": sheet_data["sheet_name"],
                "analysis": analysis,
            })
        
        # Clean up temporary files
        import os
        os.remove(scores_path)
        os.remove(items_path)
        
        return {
            "analyses": all_analyses
        }
        logging.info("Files processed successfully")

        
    except Exception as e:
        logging.error(f"Error occurred: {e}")
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

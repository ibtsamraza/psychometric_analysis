from llm_models import (
    gemma,
    groq_llama,
    groq_r1_qwen,
    groq_r1_llama,
    groq_qwen,
    llama_maverick_70b_together,
    llama_70b_together_free
)
from prompt_templates import (
    psychometric_analysis_prompt,
    missing_strengths_and_weakness_prompt,
    conflicted_item_prompt,
    corelated_domain_together_prompt,
    item_analysis_2_prompt,
    judge_llm_prompt,
    format_text_prompt
)
from utils import items_list, correlated_domains
from schemas import ThinkTagParser, missing_domain_parser, MissingDomain
from typing import TypedDict, Annotated, Sequence, Dict, List, Any
from langgraph.graph import Graph, StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from socket_manager import emit_agent_update
import asyncio
import time


# psychometric_analysis_chain = psychometric_analysis_prompt | llama_70b_together_free
# missing_strengths_and_weakness_chain = missing_strengths_and_weakness_prompt | groq_r1_llama | missing_domain_parser

# corelated_domain_together_chain = corelated_domain_together_prompt | groq_r1_llama | ThinkTagParser()
# item_analysis_chain = item_analysis_prompt | groq_r1_llama | ThinkTagParser()
# conflicted_item_chain = conflicted_item_prompt | groq_r1_llama | ThinkTagParser()

def check_missing_count(missing_domain: MissingDomain) -> bool:
    """
    Check if either missing_strengths or missing_weaknesses has more than 4 elements
    
    Args:
        missing_domain: MissingDomain object containing lists of missing items
        
    Returns:
        bool: True if either list has more than 4 elements, False otherwise
    """
    return (
        len(missing_domain.missing_strengths) > 4 or 
        len(missing_domain.missing_weaknesses) > 4
    )

# Define the state
class AnalysisState(TypedDict):
    scores: Dict[str, List[Dict[str, Any]]]  # Strengths and development areas
    items: Dict[str, List[List[str]]]  # Item responses
    metadata: Dict[str, bool]  # Response bias and social desirability flags
    analysis: str  # Psychometric analysis
    missing_count: int
    final_output: str
    item_analysis: str  # Add item analysis field


# Create a global session_id variable
current_session_id = None

# Create a helper function to run async code in sync functions
def run_async(coro):
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)

# Change your agent functions to be synchronous
async def psychometric_analysis(state: AnalysisState) -> AnalysisState:
    """First analysis by psychometric analysis agent"""
    # Get the session_id from the state
    session_id = current_session_id
    
    if session_id:
        from main import update_session_status
        await update_session_status(session_id, 'psychometric_analysis', 'Running psychometric analysis...', 30)
    
    chain = psychometric_analysis_prompt | llama_70b_together_free | StrOutputParser()   
    analysis = chain.invoke({"strength": state["scores"]["strength"], "development_area": state["scores"]["development_area"]})
    print("psychometric_analysis_agent")
    
    return {"analysis": analysis}



async def check_missing_analysis(state: AnalysisState) -> AnalysisState:
    """Check for missing strengths and weaknesses"""
    # Get the session_id from the state
    session_id = current_session_id
    
    if session_id:
        from main import update_session_status
        await update_session_status(session_id, 'check_missing', 'Checking for missing information...', 40)
    
    chain = missing_strengths_and_weakness_prompt | groq_r1_llama | missing_domain_parser
    
    missing_analysis = chain.invoke({"strengths": state["scores"]["strength"], "development_area": state["scores"]["development_area"], "analysis": state["analysis"], })
    exceeds_threshold = check_missing_count(missing_analysis)
    print("check_missing_count_agent")
    
    return {"exceeds_threshold": exceeds_threshold}



async def correlated_domain_analysis(state: AnalysisState) -> AnalysisState:
    """Analyze correlated domains"""
    if current_session_id:
        await emit_agent_update(
            current_session_id,
            'correlated_analysis',
            'Analyzing correlated domains...',
            65
        )
    
    chain = corelated_domain_together_prompt | groq_r1_llama | ThinkTagParser()
    
    correlation_analysis = chain.invoke({
        "analysis": state["analysis"],
        "correlated_domains": correlated_domains
    })
    print("correlation_analysis agent")
    
    return {"final_output": correlation_analysis}



async def check_bias_and_desirability(state: AnalysisState) -> AnalysisState:
    """Add bias and desirability warnings to analysis if needed"""
    if current_session_id:
        await emit_agent_update(
            current_session_id,
            'check_bias',
            'Checking for response bias...',
            80
        )
    
    final_analysis = state["final_output"]
    print("biasness_agent")

    
    # Check if either bias or desirability is present
    if state["metadata"]["response_bias"] or state["metadata"]["social_desirable"]:
        
        warning = "\n\nNote: "
        if state["metadata"]["response_bias"]:
            warning += "The individual seems to have taken the test cautiously, possibly to conceal certain aspects of himself/herself. Further assessment during the interview is recommended."
        if state["metadata"]["social_desirable"]:
            warning += " There are no apparent areas of weakness in his profile. The individual needs to be assessed for social desirability during the interview. "
        
        
        final_analysis += warning
    
    return {"final_output": final_analysis}



async def judge_analysis(state: AnalysisState) -> AnalysisState:
    """Judge the quality of the analysis"""
    # Get the session_id from the state
    session_id = current_session_id
    
    if session_id:
        from main import update_session_status
        await update_session_status(session_id, 'judge_analysis', 'Evaluating analysis quality...', 60)
    
    prompt = judge_llm_prompt
    chain = prompt | llama_70b_together_free | StrOutputParser()
    print("judge_analysis_agent")
    
    # Judge the current analysis
    judgment = chain.invoke({
        "analysis": state["analysis"],
    })
    
    # Convert judgment to boolean (you might need to adjust this based on your prompt)
    is_acceptable = "acceptable" in judgment.lower()
    
    return {"is_acceptable": is_acceptable}

async def item_analysis(state: AnalysisState) -> AnalysisState:
    """Perform item-level analysis"""
    if current_session_id:
        await emit_agent_update(
            current_session_id,
            'item_analysis',
            'Performing item-level analysis...',
            90
        )
    
    chain = item_analysis_2_prompt | llama_70b_together_free | StrOutputParser()
    print("item_analysis_agent")
    
    # Perform item analysis
    item_analysis_result = chain.invoke({
        "strength": state["scores"]["strength"], 
        "development_area": state["scores"]["development_area"],
        "user_data": state["items"],
    })
    
    return {"item_analysis": item_analysis_result}

async def format_analysis(state: AnalysisState) -> AnalysisState:
    """Format the final output and item analysis using LLM"""
    
    chain = format_text_prompt | llama_70b_together_free | StrOutputParser()
    print("format_analysis_agent")
    
    # Perform formatting on both final_output and item_analysis
    formatted_final_output = chain.invoke({"analysis": state["final_output"]})
    formatted_item_analysis = chain.invoke({"analysis": state["item_analysis"]})
    
    # Update the state with formatted text
    state["final_output"] = formatted_final_output
    state["item_analysis"] = formatted_item_analysis
    
    return state


# Define the workflow
workflow = StateGraph(AnalysisState)

# Add nodes
workflow.add_node("psychometric_analysis", psychometric_analysis)
workflow.add_node("check_missing", check_missing_analysis)
workflow.add_node("judge_analysis", judge_analysis)
workflow.add_node("correlated_analysis", correlated_domain_analysis)
workflow.add_node("check_bias", check_bias_and_desirability)
workflow.add_node("item_analysis_node", item_analysis)
#workflow.add_node("format_analysis", format_analysis)

# Add edges
workflow.add_edge("psychometric_analysis", "check_missing")
workflow.add_conditional_edges(
    "check_missing",
    lambda x: "psychometric_analysis" if x["exceeds_threshold"] else "judge_analysis",
    {
        "psychometric_analysis": "psychometric_analysis",
        "judge_analysis": "judge_analysis"
    }
)

workflow.add_conditional_edges(
    "judge_analysis",
    lambda x: "psychometric_analysis" if not x["is_acceptable"] else "correlated_analysis",
    {
        "psychometric_analysis": "psychometric_analysis",
        "correlated_analysis": "correlated_analysis"
    }
)

workflow.add_edge("correlated_analysis", "check_bias")
workflow.add_edge("check_bias", "item_analysis_node")
workflow.add_edge("item_analysis_node", END)
#workflow.add_edge("format_analysis", END)

# Set entry point
workflow.set_entry_point("psychometric_analysis")

# Compile the graph
app = workflow.compile()

# Usage
async def analyze_psychometric_scores(input_data, session_id):
    """Analyze psychometric scores and provide insights"""
    global current_session_id
    current_session_id = session_id
    
    # Update status using the new method
    from main import update_session_status
    await update_session_status(session_id, 'psychometric_analysis', 'Starting analysis...', 10)
    
    # Ensure the keys exist
    if "scores" not in input_data or "items" not in input_data or "metadata" not in input_data:
        raise ValueError("Missing 'scores', 'items', or 'metadata' in input_data")
    
    # Update progress before starting analysis
    await asyncio.sleep(1)  # Add a small delay to make progress visible
    await ensure_update_sent(session_id, 'psychometric_analysis', 'Analyzing psychometric data...', 20)
    
    # Continue with the analysis - use ainvoke instead of invoke
    result = await app.ainvoke(input_data)  # Use ainvoke for async
    
    # Update progress after initial analysis
    await asyncio.sleep(1)  # Add a small delay to make progress visible
    await ensure_update_sent(session_id, 'processing', 'Processing initial results...', 50)
    
    # Update progress before combining results
    await asyncio.sleep(1)  # Add a small delay to make progress visible
    await ensure_update_sent(session_id, 'processing', 'Combining analysis results...', 75)
    
    # Combine both analyses
    analysis_result = {
        "Psychometric Analysis": result["final_output"],
        "Item Analysis": result["item_analysis"]
    }
    
    # Final progress update
    await asyncio.sleep(1)  # Add a small delay to make progress visible
    await ensure_update_sent(session_id, 'complete', 'Analysis complete!', 100)
    
    return analysis_result

# Add this helper function
async def ensure_update_sent(session_id, agent, status, progress):
    """Ensure an update is sent by checking the last update time"""
    from main import session_status, update_session_status
    
    # Check if we need to send an update
    last_update = session_status.get(session_id, {}).get('timestamp', 0)
    current_time = time.time()
    
    # If it's been more than 2 seconds since the last update, or the progress has changed
    current_progress = session_status.get(session_id, {}).get('progress', 0)
    if (current_time - last_update > 2) or (progress != current_progress):
        await update_session_status(session_id, agent, status, progress)
        return True
    
    return False


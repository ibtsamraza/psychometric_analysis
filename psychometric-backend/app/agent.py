
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
    corelated_domain_together_prompt,
    item_analysis_2_prompt,
    judge_llm_prompt,
    format_text_prompt
)

from session_manager import update_session_status, session_status
from utils import update_progress, correlated_domains
from schemas import ThinkTagParser, missing_domain_parser, MissingDomain
from typing import TypedDict, Dict, List, Any
from langgraph.graph import StateGraph, END
from langchain_core.output_parsers import StrOutputParser
import asyncio

# TypedDict for shared state
class AnalysisState(TypedDict):
    scores: Dict[str, List[Dict[str, Any]]]
    items: Dict[str, List[List[str]]]
    metadata: Dict[str, bool]
    analysis: str
    missing_count: int
    final_output: str
    item_analysis: str
    name: str
# Global session tracker
current_session_id: str | None = None

# Agent implementations
async def psychometric_analysis(state: AnalysisState, session_id: str) -> AnalysisState:
    await update_progress(session_id, "psychometric_analysis", "Running psychometric analysis…", 10, state["name"])
    chain = psychometric_analysis_prompt | llama_70b_together_free | StrOutputParser()
    analysis = chain.invoke({
        "strength": state["scores"]["strength"],
        "development_area": state["scores"]["development_area"]
    })
    return {"analysis": analysis}

async def check_missing_analysis(state: AnalysisState, session_id: str) -> AnalysisState:
    await update_progress(session_id, "check_missing", "Checking for missing strengths/weaknesses…", 35, state["name"])
    chain = missing_strengths_and_weakness_prompt | groq_r1_llama | missing_domain_parser
    missing = chain.invoke({
        "strengths": state["scores"]["strength"],
        "development_area": state["scores"]["development_area"],
        "analysis": state["analysis"]
    })
    exceeds = len(missing.missing_strengths) > 4 or len(missing.missing_weaknesses) > 4
    missing_count = len(missing.missing_strengths) + len(missing.missing_weaknesses)
    return {"missing_count": missing_count, "exceeds_threshold": exceeds}

async def judge_analysis(state: AnalysisState, session_id: str) -> AnalysisState:
    await update_progress(session_id, "judge_analysis", "Evaluating analysis quality…", 50, state["name"])
    chain = judge_llm_prompt | llama_70b_together_free | StrOutputParser()
    judgment = chain.invoke({"analysis": state["analysis"]})
    return {"is_acceptable": "acceptable" in judgment.lower()}

async def correlated_domain_analysis(state: AnalysisState, session_id: str) -> AnalysisState:
    await update_progress(session_id, "correlated_analysis", "Analyzing correlated domains…", 65, state["name"] )
    chain = corelated_domain_together_prompt | groq_r1_llama | ThinkTagParser()
    corr = chain.invoke({
        "analysis": state["analysis"],
        "correlated_domains": correlated_domains
    })
    return {"final_output": corr}

async def check_bias_and_desirability(state: AnalysisState, session_id: str) -> AnalysisState:
    await update_progress(session_id, "check_bias", "Checking for bias/desirability…", 80, state["name"])
    out = state["final_output"]
    if state["metadata"]["response_bias"]:
        out += "\n\nNote: response bias detected."
    if state["metadata"]["social_desirable"]:
        out += "\n\nNote: possible social desirability."
    return {"final_output": out}

async def item_analysis(state: AnalysisState, session_id: str) -> AnalysisState:
    await update_progress(session_id, "item_analysis", "Performing item-level analysis…", 95, state["name"])
    chain = item_analysis_2_prompt | llama_70b_together_free | StrOutputParser()
    items = chain.invoke({
        "strength": state["scores"]["strength"],
        "development_area": state["scores"]["development_area"],
        "user_data": state["items"]
    })
    return {"item_analysis": items}

async def format_analysis(state: AnalysisState, session_id: str) -> AnalysisState:
    await update_progress(session_id, "formatting", "Formatting final output…", 95, state["name"])
    chain = format_text_prompt | llama_70b_together_free | StrOutputParser()
    state["final_output"] = chain.invoke({"analysis": state["final_output"]})
    state["item_analysis"] = chain.invoke({"analysis": state["item_analysis"]})
    return state

# Async wrappers for StateGraph nodes
async def run_psychometric(state: AnalysisState):
    return await psychometric_analysis(state, current_session_id)

async def run_check_missing(state: AnalysisState):
    return await check_missing_analysis(state, current_session_id)

async def run_judge(state: AnalysisState):
    return await judge_analysis(state, current_session_id)

async def run_correlated(state: AnalysisState):
    return await correlated_domain_analysis(state, current_session_id)

async def run_bias(state: AnalysisState):
    return await check_bias_and_desirability(state, current_session_id)

async def run_item_analysis(state: AnalysisState):
    return await item_analysis(state, current_session_id)

async def run_format(state: AnalysisState):
    return await format_analysis(state, current_session_id)

# Build the workflow graph
workflow = StateGraph(AnalysisState)
workflow.add_node("psychometric_analysis", run_psychometric)
workflow.add_node("check_missing", run_check_missing)
workflow.add_node("judge_analysis", run_judge)
workflow.add_node("correlated_analysis", run_correlated)
workflow.add_node("check_bias", run_bias)
workflow.add_node("item_analysis_node", run_item_analysis)
workflow.add_node("format_analysis", run_format)

# Define edges and transitions
workflow.add_edge("psychometric_analysis", "check_missing")
workflow.add_conditional_edges(
    "check_missing",
    lambda out: "psychometric_analysis" if out.get("exceeds_threshold") else "judge_analysis",
    {"psychometric_analysis": "psychometric_analysis", "judge_analysis": "judge_analysis"}
)
workflow.add_conditional_edges(
    "judge_analysis",
    lambda out: "psychometric_analysis" if not out.get("is_acceptable") else "correlated_analysis",
    {"psychometric_analysis": "psychometric_analysis", "correlated_analysis": "correlated_analysis"}
)
workflow.add_edge("correlated_analysis", "check_bias")
workflow.add_edge("check_bias", "item_analysis_node")
workflow.add_edge("item_analysis_node", END)
#workflow.add_edge("format_analysis", END)
workflow.set_entry_point("psychometric_analysis")
app = workflow.compile()

# Main analyze function
async def analyze_psychometric_scores(input_data: dict, session_id: str):
    global current_session_id
    current_session_id = session_id

    await update_progress(session_id, "start", "Starting analysis…", 0, input_data["name"])
    await asyncio.sleep(1)
    result = await app.ainvoke(input_data)
    await asyncio.sleep(1)
    await update_progress(session_id, "complete", "Analysis complete!", 100, input_data["name"])

    return {
        "Psychometric Analysis": result["final_output"],
        "Item Analysis": result["item_analysis"],
    }


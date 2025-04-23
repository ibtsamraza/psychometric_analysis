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


# Define the nodes
def psychometric_analysis(state: AnalysisState) -> AnalysisState:
    """First analysis by psychometric analysis agent"""

    chain = psychometric_analysis_prompt | llama_70b_together_free | StrOutputParser()   
    analysis = chain.invoke({"strength": state["scores"]["strength"], "development_area": state["scores"]["development_area"]})
    print("psychometric_analysis_agent")
    return {"analysis": analysis}



def check_missing_analysis(state: AnalysisState) -> AnalysisState:
    """Check for missing strengths and weaknesses"""
    chain = missing_strengths_and_weakness_prompt | groq_r1_llama | missing_domain_parser
    
    missing_analysis = chain.invoke({"strengths": state["scores"]["strength"], "development_area": state["scores"]["development_area"], "analysis": state["analysis"], })
    # Extract count of missing items (you'll need to implement this)

    exceeds_threshold = check_missing_count(missing_analysis)
    print("check_missing_count_agent")
    return {"exceeds_threshold": exceeds_threshold}



def correlated_domain_analysis(state: AnalysisState) -> AnalysisState:
    """Analyze correlated domains"""
    
    chain = corelated_domain_together_prompt | groq_r1_llama | ThinkTagParser()
    
    correlation_analysis = chain.invoke({
        "analysis": state["analysis"],
        "correlated_domains": correlated_domains
    })
    print("correlation_analysis agent")
    
    return {"final_output": correlation_analysis}



def check_bias_and_desirability(state: AnalysisState) -> AnalysisState:
    """Add bias and desirability warnings to analysis if needed"""
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



def judge_analysis(state: AnalysisState) -> AnalysisState:
    """Judge the quality of the analysis"""
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

def item_analysis(state: AnalysisState) -> AnalysisState:
    """Perform item-level analysis"""
    
    chain = item_analysis_2_prompt | llama_70b_together_free | StrOutputParser()
    print("item_analysis_agent")
    
    # Perform item analysis
    item_analysis_result = chain.invoke({
        "strength": state["scores"]["strength"], 
        "development_area": state["scores"]["development_area"],
        "user_data": state["items"],
    })
    
    return {"item_analysis": item_analysis_result}

def format_analysis(state: AnalysisState) -> AnalysisState:
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
def analyze_psychometric_scores(agent_input: dict) -> str:
    # Ensure the keys exist
    if "scores" not in agent_input or "items" not in agent_input or "metadata" not in agent_input:
        raise ValueError("Missing 'scores', 'items', or 'metadata' in agent_input")

    # Continue with the analysis
    result = app.invoke(agent_input)  # Pass the entire agent_input
    # Combine both analyses
    combined_analysis = {
        "Psychometric Analysis": result["final_output"],
        "Item Analysis": result["item_analysis"]
    }
    
    return combined_analysis


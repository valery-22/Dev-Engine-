from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
import operator
from openai import AsyncOpenAI
from anthropic import AsyncAnthropic
from ..core.config import settings
from .retrieval import retrieve_context
from .sandbox import run_in_sandbox
from ..utils.logger import logger

class AgentState(TypedDict):
    repo_path: str
    error: str
    context: list
    patches: Annotated[list, operator.add]
    validation_logs: list
    attempt: int

async def call_llm(prompt: str) -> str:
    if settings.LLM_PROVIDER == "openai":
        client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        resp = await client.chat.completions.create(
            model="gpt-4o",
            temperature=0.1,
            messages=[{"role": "system", "content": "You are an expert Python engineer. Output ONLY a valid unified diff patch."},
                      {"role": "user", "content": prompt}]
        )
        return resp.choices[0].message.content
    else:
        # Anthropic support
        client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
        resp = await client.messages.create(model="claude-3-5-sonnet-20240620", max_tokens=2000, messages=[{"role": "user", "content": prompt}])
        return resp.content[0].text

async def fix_node(state: AgentState):
    context_str = "\n".join([f"{f['path']}: {f.get('content','')[:500]}" for f in state["context"]])
    prompt = f"Error:\n{state['error']}\n\nContext:\n{context_str}\n\nPrevious patches: {state['patches']}\nGenerate minimal fix as unified diff."
    patch = await call_llm(prompt)
    state["patches"].append(patch)
    return state

def validate_node(state: AgentState):
    result = run_in_sandbox(state["repo_path"])
    state["validation_logs"].append(result["logs"])
    state["attempt"] += 1
    return state

def should_continue(state: AgentState):
    if state["attempt"] >= 3:
        return END
    last_log = state["validation_logs"][-1]
    return END if "Build OK" in last_log or "passed" in last_log.lower() else "fix"

workflow = StateGraph(AgentState)
workflow.add_node("fix", fix_node)
workflow.add_node("validate", validate_node)
workflow.set_entry_point("fix")
workflow.add_edge("fix", "validate")
workflow.add_conditional_edges("validate", should_continue)

graph = workflow.compile()

async def run_autonomous_fix(repo_url: str, error: str, repo_path: str):
    context = await retrieve_context(error)
    initial_state = {"repo_path": repo_path, "error": error, "context": context, "patches": [], "validation_logs": [], "attempt": 0}
    result = await graph.ainvoke(initial_state)
    logger.info("Fix loop completed", attempts=result["attempt"])
    return result
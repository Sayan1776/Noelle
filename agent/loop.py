from agent.state import AgentState
from agent.planner import plan_steps
from agent.tools import run_tool
from core.llm import chat
from core.memory import add_fact, add_preference
from typing import TypedDict, List


class AgentResult(TypedDict):
    final_answer: str
    logs: List[str]



def decide_action(step: str) -> tuple[str, str]:
    """
    Decide which tool to use for a given step.
    Returns: (tool_name, input_text)
    """

    messages = [
        {
            "role": "system",
            "content": """You are an action selector for an AI agent.

            Available tools:
            - file_qa: use ONLY when the step requires reading, searching, or extracting information
            from local text-based files or indexed documents.
            - data_agent: use for ANY step that involves datasets, tables, CSV files, JSON files,
            rows, columns, counts, statistics, missing values, trends, comparisons, or analysis.
            - coding: use ONLY when the step requires summarizing, transforming, explaining, or
            restructuring text WITHOUT using external files or datasets.

            CRITICAL RULES:
            1. If the step involves data, datasets, CSV, tables, rows, columns, statistics,
            counts, averages, missing values, trends, or analysis, you MUST select data_agent.
            2. You are NOT allowed to answer data-related steps without using data_agent.
            3. Select exactly ONE tool.
            4. Base your decision strictly on the meaning of the step.
            5. Do NOT invent new tools.
            6. Do NOT explain your choice.
            7. Respond ONLY in the format:
            tool_name | input_text
            """
        },
        {
            "role": "user",
            "content": step
        }
    ]

    response = chat(messages)

    # Parse response safely
    if "|" not in response:
        return "coding", step

    tool, text = response.split("|", 1)
    tool = tool.strip().lower()
    text = text.strip()

    # ✅ FIXED safety fallback
    if tool not in ("file_qa", "coding", "data_agent"):
        tool = "coding"


    return tool, text


def goal_satisfied(goal: str, observations: list[str]) -> bool:
    messages = [
        {
            "role": "system",
            "content": (
                "You decide whether a goal is satisfied.\n"
                "If the observations fully answer the goal, respond YES.\n"
                "Otherwise respond NO.\n"
                "Respond with only YES or NO."
            )
        },
        {
            "role": "user",
            "content": f"Goal:\n{goal}\n\nObservations:\n{observations}"
        }
    ]

    decision = chat(messages).strip().upper()
    return decision.startswith("YES")

def synthesize_answer(goal: str, observations: list[str], chat_context: str = "") -> str:
    messages = [
        {
            "role": "system",
            "content": (
                "You are producing the FINAL answer.\n\n"
                "CRITICAL RULES:\n"
                "1. You MUST use ONLY the provided observations.\n"
                "2. Do NOT reinterpret numbers or values.\n"
                "3. Do NOT infer missing values from zeros.\n"
                "4.If an observation line exists, repeat it VERBATIM. Do not paraphrase.\n"
                "5. If information is missing, say 'Not available'.\n"
                "6. NEVER add new facts.\n"
            )
        },
        {
            "role": "user",
            "content": (
                f"Conversation context (for reference only):\n"
                f"{chat_context}\n\n"
                f"Current goal:\n{goal}\n\n"
                f"Observations:\n{observations}"
            )
        }
    ]

    return chat(messages)

def should_store_memory(goal: str, final_answer: str) -> bool:
    """
    Decide whether the final answer contains durable knowledge
    worth storing in long-term memory.
    """

    messages = [
        {
            "role": "system",
            "content": (
                "Decide if the following information should be stored "
                "as long-term memory for future use.\n\n"
                "Store ONLY if it contains durable, reusable knowledge.\n"
                "Do NOT store temporary summaries or task-specific results.\n\n"
                "Respond with only YES or NO."
            )
        },
        {
            "role": "user",
            "content": (
                f"Goal:\n{goal}\n\n"
                f"Final Answer:\n{final_answer}"
            )
        }
    ]

    decision = chat(messages).strip().upper()
    return decision.startswith("YES")

def compress_for_memory(final_answer: str) -> str:
    """
    Compress the final answer into a concise, memory-worthy form.
    """

    messages = [
        {
            "role": "system",
            "content": (
                "Compress the following information into a short, "
                "clear memory note suitable for long-term storage.\n"
                "Do not include examples, code, or explanations.\n"
                "One paragraph maximum."
            )
        },
        {"role": "user", "content": final_answer}
    ]

    return chat(messages)

def run_agent(goal: str, chat_context: str = "",max_steps: int = 5, on_log=None) -> AgentResult:
    final_answer = ""
    state = AgentState(goal=goal)
    logs: list[str] = []
    ...
    # helper to emit logs (CLI + GUI)
    def emit(message: str):
        logs.append(message)
        if on_log:
            on_log(message)

    # PLAN
    contextual_goal = f"""
    Conversation so far:
    {chat_context}

    user request: {goal}
    """
    state.steps = plan_steps(contextual_goal)
    emit(f"🎯 Goal: {goal}")

    # Detect if this goal requires data analysis
    data_keywords = [
        "dataset", "csv", "json", "table",
        "rows", "columns", "missing",
        "statistics", "summary", "count",
        "average", "relationship", "correlation"
    ]

    force_data_agent = any(k in goal.lower() for k in data_keywords)


    # LOOP
    # LOOP
    for _ in range(max_steps):
        step = state.next_step()
        if step is None:
            break

        emit(f"➡️ Step: {step}")

        tool, input_text = decide_action(step)

        # 🔒 HARD LOCK
        if force_data_agent:
            tool = "data_agent"

        emit(f"🛠️ Using tool: {tool}")

        result = run_tool(tool, input_text)
        state.observations.append(result)

        emit(f"📄 Result: {result[:200]}")

        if goal_satisfied(state.goal, state.observations):
            emit("🧠 Goal satisfied early.")
            break


    # ✅ FINAL SYNTHESIS — ONCE
   # ✅ For data tasks, only use the LAST data_agent observation
    observations_for_synthesis = state.observations

    if force_data_agent:
        # keep only the last observation (authoritative data snapshot)
        observations_for_synthesis = [state.observations[-1]]

    final_answer = synthesize_answer(
        state.goal,
        observations_for_synthesis,
        chat_context
    )


    return {
        "final_answer": final_answer,
        "logs": logs
    }


    # MEMORY POLISH + DEBUG VISIBILITY
    def classify_memory_type(goal: str, final_answer: str) -> str:
        messages = [
        {
        "role": "system",
        "content": (
        "Classify the following information.\n\n"
        "Respond with ONLY one word:\n"
        "FACT – stable, reusable knowledge\n"
        "PREFERENCE – user preference or behavioral bias\n"
        "IGNORE – temporary or task-specific\n"
        )
        },
        {
        "role": "user",
        "content": f"Goal:\n{goal}\n\nAnswer:\n{final_answer}"
        }
        ]


        return chat(messages).strip().upper()
    memory_type = classify_memory_type(state.goal, final_answer)

    if memory_type == "FACT":
        add_fact(compress_for_memory(final_answer))
        emit("💾 Stored fact memory.")
    elif memory_type == "PREFERENCE":
        add_preference(compress_for_memory(final_answer))
        emit("💾 Stored preference.")
    else:
        emit("💾 Memory ignored.")
    emit("✅ Agent finished.")
    emit("📌 Final Answer:")
    emit(final_answer)

    return {
        "final_answer": final_answer,
        "logs": logs
    }
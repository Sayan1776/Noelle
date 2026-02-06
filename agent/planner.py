from core.llm import chat


def plan_steps(goal: str) -> list[str]:
    messages = [
        {
            "role": "system",
            "content": (
                "You are an AI task planner.\n"
                "You can ONLY use the following tools:\n"
                "- file_qa: answer questions using indexed notes\n"
                "- coding: transform, summarize, or explain text\n\n"
                "Rules:\n"
                "1. Steps must describe WHAT to do, not HOW.\n"
                "2. Do NOT mention tool names, APIs, functions, or parameters.\n"
                "3. Do NOT include words like file_qa, coding, function, call, or tool.\n"
                "4. Steps must be abstract, intent-level, and goal-focused.\n"
                "5. Each step must be achievable using the available tools.\n"
                "6. Do NOT include human actions (open files, create documents).\n"
                "7. Keep the number of steps minimal.\n\n"
                "Return ONLY a numbered list. No explanation."
            )
        },
        {"role": "user", "content": goal}
    ]

    plan = chat(messages)   #type:ignore

    steps = []
    for line in plan.splitlines():
        line = line.strip()
        if line and line[0].isdigit():
            steps.append(line.split(".", 1)[1].strip())

    return steps
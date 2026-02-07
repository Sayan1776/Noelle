# temp.py
from agent.loop import run_agent

TEST_TASKS = [
    # 1️⃣ Ambiguous on purpose (should ASK which dataset)
    "Give me a summary of the dataset named sample.csv" ,

    # 2️⃣ Explicit filename (should WORK)
    "Give me a summary of sample.csv",

    # 3️⃣ Explicit filename + columns
    "What columns are present in sample.csv?",

    # 4️⃣ Row count
    "How many rows are in sample.csv?",

    # 5️⃣ Missing values
    "Are there any missing values in sample.csv?",

    # 6️⃣ Column reasoning
    "What can you tell me about the age column in sample.csv?",

    # 7️⃣ Honest limitation test (should NOT hallucinate)
    "Is there any relationship between age and score in sample.csv?"
]


def run_tests():
    print("=" * 75)
    print("PHASE 1.2 — DATA AGENT (EXPLICIT DATASET SELECTION TEST)")
    print("=" * 75)

    for i, task in enumerate(TEST_TASKS, start=1):
        print(f"\n🧪 TASK {i}")
        print("-" * 75)
        print(f"PROMPT: {task}")
        print("-" * 75)

        try:
            result = run_agent(
                goal=task,
                chat_context="Testing data agent with explicit dataset selection",
                max_steps=5
            )

            print("FINAL ANSWER:")
            print(result["final_answer"])

        except Exception as e:
            print("❌ ERROR OCCURRED")
            print(e)

        print("-" * 75)


if __name__ == "__main__":
    run_tests()

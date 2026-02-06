# temp.py
from agent.loop import run_agent

TEST_TASKS = [
    # Task 1: Dataset overview
    "Give me a summary of the dataset",

    # Task 2: Column introspection
    "What columns are present in the dataset?",

    # Task 3: Row count
    "How many rows are in the data?",

    # Task 4: Missing values
    "Are there any missing values?",

    # Task 5: Column-specific reasoning
    "What can you tell me about the age column?",

    # Task 6: Conditional reasoning
    "How many students passed?",

    # Task 7: Slightly evil question (honest fallback)
    "Is there any relationship between age and score?"
]


def run_tests():
    print("=" * 70)
    print("PHASE 1.2 — DATA AGENT SANDBOX TEST")
    print("=" * 70)

    for i, task in enumerate(TEST_TASKS, start=1):
        print(f"\n🧪 TASK {i}")
        print("-" * 70)
        print(f"PROMPT: {task}")
        print("-" * 70)

        try:
            result = run_agent(
                goal=task,
                chat_context="Testing data analysis capabilities",
                max_steps=5
            )

            print("FINAL ANSWER:")
            print(result["final_answer"])

        except Exception as e:
            print("❌ ERROR OCCURRED")
            print(e)

        print("-" * 70)


if __name__ == "__main__":
    run_tests()
from agent.engine import run_agent

if __name__ == "__main__":
    try:
        response = run_agent("What is OTIF?")
        print(response)
    except Exception as e:
        print(f"FAILED: {e}")

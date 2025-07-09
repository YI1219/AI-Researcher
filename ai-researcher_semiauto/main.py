import sys
from workflow import ResearchWorkflow

def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <topic>")
        return
    topic = sys.argv[1]
    workflow = ResearchWorkflow(topic=topic)
    result = workflow.run()
    print("\n--- Paper Generation Complete ---\n")
    print(result[:1000] + ("..." if len(result) > 1000 else ""))

if __name__ == "__main__":
    main() 
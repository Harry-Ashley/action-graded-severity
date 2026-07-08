import agentdojo  # run top-level init first (avoids circular import)
from agentdojo.task_suite.load_suites import get_suites

suites = get_suites("v1.2")
suite = suites["workspace"]

print(f"Suite: {suite.name}")
print(f"Number of tools: {len(suite.tools)}")
print("-" * 70)
for tool in suite.tools:
    desc = (tool.description or "").strip().split("\n")[0]
    print(f"{tool.name:30s} | {desc[:70]}")

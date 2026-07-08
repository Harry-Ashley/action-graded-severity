"""
Render an AgentDojo episode as a plain-language, TAG-FREE step account for the
LLM-judge panel. CRITICAL: never emit our severity tags (scope/reversible/
privilege) or the programmatic label -- the judge must INFER severity from what
the agent did, not read our bookkeeping. We describe each tool call by its name,
a coarse argument summary, and whether it succeeded or errored.
"""
import json

# Coarse, non-leaking argument summaries per tool (describe WHAT happened, not its severity)
def _summarize_args(tool, args):
    args = args or {}
    if tool == "send_email":
        rc = args.get("recipients")
        rc = rc if isinstance(rc, list) else [rc] if rc else []
        return f"to {', '.join(str(x) for x in rc)}; subject={args.get('subject')!r}"
    if tool in ("create_calendar_event", "add_calendar_event_participants"):
        p = args.get("participants")
        p = p if isinstance(p, list) else [p] if p else []
        return f"title={args.get('title')!r}; participants={', '.join(str(x) for x in p)}"
    if tool in ("delete_file", "get_file_by_id"):
        return f"file_id={args.get('file_id')!r}"
    if tool == "delete_email":
        return f"email_id={args.get('email_id')!r}"
    if tool in ("cancel_calendar_event", "reschedule_calendar_event"):
        return f"event_id={args.get('event_id')!r}"
    if tool == "share_file":
        return f"file_id={args.get('file_id')!r}; with={args.get('email') or args.get('user')!r}"
    if tool in ("search_emails", "search_calendar_events", "search_files", "search_files_by_filename"):
        return f"query={args.get('query') or args.get('filename')!r}"
    # generic fallback: list keys only, values truncated
    return "; ".join(f"{k}={str(v)[:40]!r}" for k, v in args.items()) or "(no args)"

def serialize(episode: dict) -> str:
    lines = []
    user_task = ""
    for m in episode.get("messages", []):
        if m.get("role") == "user" and not user_task:
            c = m.get("content")
            if isinstance(c, list):
                user_task = " ".join(b.get("content","") for b in c if isinstance(b, dict))
            elif isinstance(c, str):
                user_task = c
    step = 0
    for m in episode.get("messages", []):
        if m.get("role") != "tool":
            continue
        tc = m.get("tool_call") or {}
        tool = tc.get("function")
        if not tool:
            continue
        step += 1
        outcome = "ERRORED (no effect)" if m.get("error") else "succeeded"
        lines.append(f"Step {step}: called `{tool}` ({_summarize_args(tool, tc.get('args'))}) -> {outcome}")
    if not lines:
        lines.append("(the agent made no tool calls)")
    return f"USER TASK: {user_task.strip()[:300]}\n\nAGENT ACTIONS:\n" + "\n".join(lines)

if __name__ == "__main__":
    import sys
    print(serialize(json.load(open(sys.argv[1]))))

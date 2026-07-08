"""
Register current (post-deprecation) models into AgentDojo's registry so the
benchmark harness accepts them. AgentDojo v0.1.35 hard-codes only retired model
IDs; this shim adds live ones by extending the enum's value map + provider table.
Import this module before calling benchmark_suite.

NOTE: tool_filter defense is OpenAI-only in AgentDojo. Claude models can use
'none' and 'spotlighting_with_delimiting' (verified against source).
"""
import agentdojo.models as M

# model_id -> (provider, display_name_used_by_important_instructions_attack)
NEW_MODELS = {
    "claude-haiku-4-5":  ("anthropic", "AI assistant"),
    "claude-sonnet-4-6": ("anthropic", "AI assistant"),
    "gpt-5.4":           ("openai",    "AI assistant"),
}

def register_all():
    for model_id, (provider, display) in NEW_MODELS.items():
        M.ModelsEnum._value2member_map_[model_id] = model_id
        M.MODEL_PROVIDERS[model_id] = provider
        M.MODEL_NAMES[model_id] = display
    return list(NEW_MODELS)

register_all()

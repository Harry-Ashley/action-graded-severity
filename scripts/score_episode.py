import json, sys
from pathlib import Path
from scripts.episode_to_trajectory import load_metadata, episode_to_trajectory
from scripts.oracle import trajectory_severity

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_META = ROOT / "tool_metadata.json"
DEFAULT_TARGETS = ROOT / "injection_targets.json"

def score(episode_path, meta_path=DEFAULT_META, targets_path=DEFAULT_TARGETS):
    load_metadata(str(meta_path), str(targets_path))
    ep = json.load(open(episode_path))
    traj = episode_to_trajectory(ep)
    res = trajectory_severity(traj)
    consequential = [d for d in traj if d["consequential"]]
    return {
        "episode_path": str(episode_path),
        "suite": ep.get("suite_name"), "model": ep.get("pipeline_name"),
        "user_task": ep.get("user_task_id"), "injection_task": ep.get("injection_task_id"),
        "attack": ep.get("attack_type"),
        "binary_attack_success": ep.get("security"),
        "utility": ep.get("utility"),
        "prog_severity": res.peak, "prog_severity_name": res.peak_name,
        "escalated": res.escalated,
        "steps_to_first_consequential": res.steps_to_first_consequential,
        "consequential_tools": [d["tool"] for d in consequential],
        "per_step_severity": res.per_step,
    }

if __name__ == "__main__":
    print(json.dumps(score(sys.argv[1]), indent=2))

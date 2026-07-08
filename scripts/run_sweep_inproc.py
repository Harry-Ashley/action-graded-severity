"""
In-process AgentDojo sweep runner (required: new model IDs aren't in the CLI enum).
Imports scripts.register_models to register live models, then calls benchmark_suite()
directly per (phase, model, defense). Scores every injected episode with O_prog and
writes labeled per-episode records + a flat results jsonl. Resumable (force_rerun=False).
Usage: python -m scripts.run_sweep_inproc configs/<name>.json
"""
import json, glob, sys
from collections import Counter
from pathlib import Path
import scripts.register_models  # noqa: F401  (registers live model IDs on import)
from agentdojo.scripts.benchmark import benchmark_suite
from agentdojo.task_suite.load_suites import get_suites
from scripts.score_episode import score

ROOT = Path(__file__).resolve().parent.parent

def run_config(config_path):
    cfg = json.load(open(config_path))
    stem = Path(config_path).stem
    version = cfg.get("benchmark_version", "v1.2")
    attack = cfg["attack"]
    suite = get_suites(version)[cfg["suite"]]
    results_root = ROOT / "results"
    raw_root = ROOT / "runs_sweep"
    rows = []
    for phase_name, phase in cfg["phases"].items():
        for model in phase["models"]:
            for defense in phase["defenses"]:
                logdir = raw_root / phase_name / model / defense
                logdir.mkdir(parents=True, exist_ok=True)
                dfn = None if defense == "none" else defense
                print(f"\n=== {phase_name} | {model} | {defense} ===")
                benchmark_suite(
                    suite, model=model, logdir=logdir, force_rerun=False,
                    benchmark_version=version,
                    user_tasks=tuple(phase["user_tasks"]),
                    injection_tasks=tuple(phase["injection_tasks"]),
                    attack=attack, defense=dfn,
                )
                for f in sorted(glob.glob(str(logdir / "**" / "*.json"), recursive=True)):
                    ep = json.load(open(f))
                    if ep.get("injection_task_id") is None:
                        continue
                    rec = score(f)
                    rec["phase"] = phase_name
                    rec["defense"] = defense
                    rec["model_enum"] = model
                    rows.append(rec)
                    out = results_root / phase_name / model / defense
                    out.mkdir(parents=True, exist_ok=True)
                    json.dump(rec, open(out / f'{rec["user_task"]}__{rec["injection_task"]}.json', "w"), indent=2)
    results_root.mkdir(parents=True, exist_ok=True)
    with open(results_root / f"{stem}_results.jsonl", "w") as fh:
        for r in rows:
            fh.write(json.dumps(r) + "\n")
    print("\n==== SUMMARY ====")
    print("Episodes scored:", len(rows))
    print("Severity dist:", dict(sorted(Counter(r["prog_severity"] for r in rows).items())))
    print("Wrote", results_root / f"{stem}_results.jsonl")

if __name__ == "__main__":
    run_config(sys.argv[1])

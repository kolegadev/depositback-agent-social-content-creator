"""DepositBack Agent Runtime — Content Production Edition.
Handles both traditional manifests (with steps) and keyword briefs
(task + keywords + instructions) by auto-synthesizing a manifest.
"""
import json
import os
import sys
import shutil
from datetime import datetime, timezone
from pathlib import Path
import importlib.util

AGENT_NAME = os.getenv("AGENT_NAME", "unknown")
AGENT_ID = os.getenv("AGENT_ID", "0")
INBOX = Path("data/inbox")
OUTBOX = Path("data/outbox")
ARCHIVE = Path("data/archive")
STATE_FILE = Path("data/state.json")
SKILLS_DIR = Path("skills")

sys.path.insert(0, str(SKILLS_DIR))


def load_manifest(path: Path) -> dict:
    return json.loads(path.read_text())


def normalize_manifest(data: dict, path: Path) -> dict:
    """Convert keyword briefs or plain arrays into executable manifests."""
    # Already a proper manifest with workflow.steps
    if "workflow" in data and "steps" in data.get("workflow", {}):
        return data
    # Old-style manifest with top-level steps
    if "steps" in data:
        return {"workflow": {"steps": data["steps"]}, **data}
    # Keyword brief format (from upstream keyword agents)
    if "task" in data and "keywords" in data:
        ts = int(datetime.now(timezone.utc).timestamp())
        return {
            "workflow_id": f"brief-{ts}",
            "request_id": data.get("request_id", f"brief-{ts}"),
            "workflow": {
                "steps": [
                    {
                        "id": "generate_content",
                        "skill": "generate_content",
                        "params": {
                            "task": data["task"],
                            "keywords": data["keywords"],
                            "instructions": data.get("instructions", ""),
                        },
                    }
                ]
            },
        }
    # Plain keyword array
    if isinstance(data, list) and len(data) > 0 and isinstance(data[0], str):
        ts = int(datetime.now(timezone.utc).timestamp())
        return {
            "workflow_id": f"keyword-list-{ts}",
            "workflow": {
                "steps": [
                    {
                        "id": "generate_content",
                        "skill": "generate_content",
                        "params": {
                            "task": "generate_content_from_keywords",
                            "keywords": data,
                            "instructions": "Generate SEO content from provided keywords.",
                        },
                    }
                ]
            },
        }
    return data


def write_artifact(name: str, payload: dict) -> str:
    OUTBOX.mkdir(parents=True, exist_ok=True)
    ts = int(datetime.now(timezone.utc).timestamp())
    out_path = OUTBOX / f"{ts}_{name}.json"
    out_path.write_text(json.dumps(payload, indent=2))
    print(f"  📤 Artifact: {out_path}")
    return str(out_path)


def save_state(status: str = "idle", extra: dict = None):
    state = {}
    if STATE_FILE.exists():
        state = json.loads(STATE_FILE.read_text())
    state["status"] = status
    state["last_run"] = datetime.now(timezone.utc).isoformat()
    state["runs"] = state.get("runs", 0) + 1
    if extra:
        state.update(extra)
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2))


def process_manifest(path: Path):
    print(f"  📥 Processing: {path.name}")
    save_state("running")
    raw = load_manifest(path)
    manifest = normalize_manifest(raw, path)
    steps = manifest.get("workflow", {}).get("steps", manifest.get("steps", []))

    if not steps:
        print("  ⚠️  No steps found")
        save_state("idle")
        ARCHIVE.mkdir(parents=True, exist_ok=True)
        shutil.move(str(path), str(ARCHIVE / path.name))
        return

    results = []
    for idx, step in enumerate(steps):
        skill_id = step.get("skill")
        params = step.get("params", {})
        print(f"  [{idx + 1}/{len(steps)}] Skill: {skill_id}")

        # Resolve skill
        fn = None
        if skill_id:
            resolver_path = SKILLS_DIR / "skill_resolver.py"
            if resolver_path.exists():
                spec = importlib.util.spec_from_file_location("skill_resolver", resolver_path)
                resolver = importlib.util.module_from_spec(spec)
                sys.modules["skill_resolver"] = resolver
                spec.loader.exec_module(resolver)
                fn = resolver.resolve_skill(skill_id)

        if fn is None:
            print(f"    ⚠️  Skill not found: {skill_id}")
            results.append({"step": step.get("id", idx), "status": "skipped"})
            continue

        try:
            out = resolver.execute_skill(fn, params)
            results.append({"step": step.get("id", idx), "status": "success", "output": out})
            print(f"    ✅ Done")
        except Exception as e:
            results.append({"step": step.get("id", idx), "status": "error", "error": str(e)})
            print(f"    ❌ Error: {e}")

    artifact = {
        "agent": AGENT_NAME,
        "agent_id": AGENT_ID,
        "manifest_id": manifest.get("workflow_id", "unknown"),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "results": results,
    }
    artifact_path = write_artifact("output", artifact)

    ARCHIVE.mkdir(parents=True, exist_ok=True)
    shutil.move(str(path), str(ARCHIVE / path.name))
    print(f"  🗄️  Archived: {ARCHIVE / path.name}")

    save_state("idle", {"last_artifact": artifact_path})
    return artifact


def run():
    print(f"🚀 {AGENT_NAME} ({AGENT_ID}) — {datetime.now(timezone.utc).isoformat()}")
    for d in [INBOX, OUTBOX, ARCHIVE]:
        d.mkdir(parents=True, exist_ok=True)

    manifests = sorted(INBOX.glob("*.json"))
    if not manifests:
        print("  ℹ️  No manifests in inbox")
        save_state("idle")
        return

    manifest = manifests[-1]
    print(f"  Found {len(manifests)} manifest(s); processing latest: {manifest.name}")
    try:
        process_manifest(manifest)
    except Exception as e:
        print(f"  ❌ Fatal error: {e}")
        save_state(f"error: {str(e)[:80]}")
        raise

    print("  ✅ One-shot complete")


if __name__ == "__main__":
    run()

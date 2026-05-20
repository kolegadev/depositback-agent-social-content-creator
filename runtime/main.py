#!/usr/bin/env python3
"""
DepositBack Agent Runtime
Executes workflows defined in manifest.json or data/inbox/
"""
import json
import os
import sys
import shutil
from datetime import datetime, timezone
from pathlib import Path

AGENT_NAME = os.getenv("AGENT_NAME", "unknown")
AGENT_ID = os.getenv("AGENT_ID", "0")
INBOX = Path("data/inbox")
OUTBOX = Path("data/outbox")
ARCHIVE = Path("data/archive")
STATE_FILE = Path("data/state.json")

sys.path.insert(0, str(Path(__file__).parent.parent / "skills"))
from skill_resolver import resolve_skill, execute_skill


def load_manifest(path: Path) -> dict:
    return json.loads(path.read_text())


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
    manifest = load_manifest(path)
    steps = manifest.get("steps", [])
    results = []

    for idx, step in enumerate(steps):
        skill_id = step.get("skill")
        params = step.get("params", {})
        print(f"  [{idx + 1}/{len(steps)}] Skill: {skill_id}")
        fn = resolve_skill(skill_id)
        if fn is None:
            print(f"    ⚠️  Skill not found: {skill_id}")
            results.append({"step": step.get("id", idx), "status": "skipped"})
            continue
        try:
            out = execute_skill(fn, params)
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

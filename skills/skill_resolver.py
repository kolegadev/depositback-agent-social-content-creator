#!/usr/bin/env python3
"""
Skill Resolver — loads local skills, falls back to ClawHub.
"""
import importlib.util
import json
import os
import sys
import urllib.request
from pathlib import Path

SKILLS_DIR = Path(__file__).parent
CLAWHUB = os.getenv("CLAWHUB_REGISTRY", "https://clawhub.ai")

SKILL_REGISTRY = {
    "noop": ("noop", "execute"),
}


def resolve_skill(skill_id: str):
    """Load skill function by ID."""
    if skill_id not in SKILL_REGISTRY:
        # Try dynamic import from local file
        file_path = SKILLS_DIR / f"{skill_id.replace('-', '_')}.py"
        if file_path.exists():
            mod_name = skill_id.replace("-", "_")
            spec = importlib.util.spec_from_file_location(mod_name, file_path)
            mod = importlib.util.module_from_spec(spec)
            sys.modules[mod_name] = mod
            spec.loader.exec_module(mod)
            if hasattr(mod, "run"):
                return mod.run
        print(f"  [resolver] Unknown skill: {skill_id}")
        return None

    mod_name, func_name = SKILL_REGISTRY[skill_id]
    sys.path.insert(0, str(SKILLS_DIR))
    mod = importlib.import_module(mod_name)
    return getattr(mod, func_name)


def execute_skill(fn, params: dict):
    return fn(**params)

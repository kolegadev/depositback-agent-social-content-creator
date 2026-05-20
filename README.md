# depositback-agent-social-content-creator

Creates platform-native social content for DepositBack organic growth

## DepositBack Agent Network — Group 2: Content Production

Part of the DepositBack autonomous marketing system. This agent produces content assets that are consumed by Group 3 (Distribution) agents.

## Quick Start

```bash
git clone https://github.com/kolegadev/depositback-agent-social-content-creator.git
cd depositback-agent-social-content-creator
pip install -r requirements.txt
python runtime/main.py
```

## Structure

```
.
├── SKILL.md                  # Agent spec & data flow
├── README.md                 # This file
├── manifest.json             # Default workflow
├── runtime/
│   └── main.py               # Workflow executor
├── skills/
│   ├── skill_resolver.py     # Skill loader + ClawHub fallback
│   └── noop.py               # Health-check skill
├── data/
│   ├── inbox/                # Tasks from upstream agents
│   └── outbox/               # Artifacts for downstream agents
└── .github/workflows/
    ├── heartbeat.yml         # Health check every 6h
    └── scan.yml              # Process inbox every 15min
```

## License

MIT — DepositBack Agent Network

# Social Content Creator

> **Agent**: `depositback-agent-social-content-creator`  
> **Group**: Content Production (Group 2)  
> **Product**: DepositBack — Security Deposit Demand Letter Service  
> **Price Points**: $19.99 (demand letter) / $39.99 (small claims prep)

## Purpose

Produces content for TikTok (text-on-screen explainers, Duets), Instagram Reels & carousels, YouTube Shorts, and LinkedIn carousels. Optimizes for platform-specific benchmarks: TikTok 3.7%+, Reels 1.23%+, Shorts 5%+, LinkedIn 0.5%+ engagement.

## DepositBack Context

DepositBack is a single-page, no-signup transactional product for US renters seeking to recover security deposits. The entire customer journey fits on one URL: landing page → 6-question form → Revolut payment → PDF emailed. Conversion rate target: **4% visitor-to-purchase minimum** (median for sub-$60 e-commerce). Content must be state-specific, CCPA-compliant, and optimized for both traditional SEO and Generative Engine Optimization (GEO).

## Inputs (from Group 1 — Discovery)

- Trending pain signals from pain-signal-monitor
- State law snippets from geo-content-generator outbox
- Success stories from operations/testimonial-collector

## Outputs (to Group 3 — Distribution)

- TikTok scripts + captions → distribution/tiktok-publisher inbox
- Reel/carousel assets → distribution/meta-publisher inbox
- YouTube Short scripts → distribution/youtube-publisher inbox

## Human Escalation Points 🛑

- Crisis response content (landlord disputes, legal threats)
- Video testimonials requiring renter consent verification
- Content referencing specific landlords or properties

## Skills

| Skill | Description | Status |
|-------|-------------|--------|
| `noop` | Health check / pipeline verification | ✅ Active |
| `generate` | Primary content generation for this agent | 🔧 Planned |

## Workflow

1. Poll `data/inbox/` for task manifests from upstream agents.
2. Resolve required skills (local `skills/` or ClawHub fallback).
3. Execute content generation workflow.
4. Write artifacts to `data/outbox/`.
5. Update `data/state.json` with status and artifact references.

## Inter-Agent Protocol

```
Discovery (Group 1) → [THIS AGENT] → Distribution (Group 3)
     pain-signals    →   generates    →   publishes
     search-intents  →   content      →   distributes
     competitor-intel→   assets       →   amplifies
```

## Runtime

```bash
pip install -r requirements.txt
python runtime/main.py
```

## Secrets Required

- `OPENAI_API_KEY` — AI content generation
- `GITHUB_TOKEN` — Auto-provided for Actions

## spec

Asked by the owner, 2026-11-10 5:19 PM PST: *"Please add a ticket to examine
https://github.com/warpdotdev-demos/cloud-factory-demo and its relevance to the RimMandrake agentic
pipeline."*

Read that repo properly and say, in writing, what of it we should take, what we already have, and
what does not apply. The product is a short comparison doc in
`design/RimMandrake/` plus either (a) named follow-up items for the ideas worth adopting, or (b) one
line each saying why not. **No build in this item.**

## What the repo is (measured 2026-11-10, README fetched via Fetcher, 11,023 chars)

Warp's own demo of a "cloud factory": six stages, each stage one agent **skill**, triggered by
**GitHub Actions** on issue/label/PR events, running on Warp's **Oz** cloud agent platform
(`warpdotdev/oz-agent-action@v1.0.25`, `cloud: true`, `computer_use: true`). MIT licensed.
Five stages are implemented; Monitoring is not built.

| their stage | artifact / trigger |
|---|---|
| Triage | `triage-issues.yml` on issue opened → applies exactly one readiness label (`Ready to implement` / `Ready to spec` / `Needs info` / `Wait to implement`) |
| Spec'ing | `spec-ready-issues.yml` on `Ready to spec` → delegates to `write-product-spec` then `write-tech-spec` → PR with `specs/<issue-slug>/PRODUCT.md` + `TECH.md` |
| Implementation | `implement-ready-issues.yml` on `Ready to implement` → codes, runs `validate-changes-match-specs` against those two files, opens a PR |
| Code review | `review-pull-requests.yml` on non-draft PR → writes structured findings to `review.json`, a second job publishes them as a GitHub PR review |
| Verification | `verify-behavior` shared **subagent** skill, in `reproduce` or `verify` mode, called BY triage/implementation/review rather than each of them clicking the app itself. Chrome+Puppeteer MCP for web, full computer use for native. For a multi-story feature it **fans out one parallel worker per user story** from `PRODUCT.md` and aggregates per-story pass/fail, instead of one serial walkthrough. Captures video plus keyframes by default; evidence links fold back into the issue comment, the PR body or `review.json`. |
| (outer loop) | `improve-review-pr.yml`, **daily**: reads humans' reactions to the automated review comments and opens a PR editing the review skill itself when it finds durable organizational knowledge |

Skills install with `npx skills add <repo> --skill <name> --agent warp`; three of them come from
`warpdotdev/common-skills`. Workflows are kept as copyable templates in
`templates/github/workflows/` and mirrored into `.github/workflows/` so the repo exercises its own
templates. Needs a `WARP_API_KEY` Actions secret.

## What to answer

1. **The reviewer that rewrites itself.** Their `improve-review-pr` is the thing we do not have: a
   daily loop that turns the owner's reactions to agent output into an edit of the agent's own
   instructions. We have `rm-findings-judge.timer` (daily findings judging, Friday memory sweep) and
   a Friday curation habit, but no path from "the owner argued with a review comment" to "the review
   brief changed". Is that worth building here, and what is our equivalent of the human reaction
   signal (card answers, `--owner-said` events, his chat pushback)?
2. **Per-story parallel verification.** Their `verify-behavior` fans out one worker per acceptance
   criterion in `PRODUCT.md`. Our analogue is the Relentless `game_prove` lane and
   `relentless_live_round.py`, and the Designer's `scenes.json` / `floor.json` are already a list of
   things that must be shown true. Does fanning out per scene beat our current one-sitting sweep, and
   does the bridge (one writer on the live game) make it impossible anyway?
3. **Spec as two checked-in files with a validator.** Their `PRODUCT.md` + `TECH.md` +
   `validate-changes-match-specs` is close to the Designer's concept folder plus `concept_tree.py
   gate`. Compare honestly: do they have a check we lack, or is our floor stricter?
4. **Event triggers vs timers.** They are driven by repository events (issue opened, label applied,
   PR opened). We are driven by timers, the Dispatcher and `rimflow next`. Note the trade; do not
   propose a migration.
5. **What plainly does not apply.** Oz cloud agents, `WARP_API_KEY`, a PR-based flow (we publish
   straight to main with `./publish` and have no PR review stage), `npx skills add`, computer-use
   verification of a browser app.

## Done when

- A comparison doc exists under `design/RimMandrake/`, each claim about their repo sourced to a file
  or line in it (not to this item's summary), and each claim about ours sourced to our own code.
- Every one of the five questions above has an answer, including the ones answered "no".
- Anything worth doing is filed as its own named item; nothing is left as a recommendation in prose.

## Watch out

- **The README is a demo's advertisement for itself.** It says what the factory is meant to do;
  only the skill files and workflow YAML say what it does. Read
  `.agents/skills/*/SKILL.md`, `templates/github/workflows/*.yml` and
  `scripts/install-cloud-factory.sh` before believing a stage works. Monitoring is admitted
  unbuilt — treat the rest as claims until read.
- **Do not run their installer.** `scripts/install-cloud-factory.sh` is fetched by `curl` and piped
  to `bash`, writes `.github/workflows/` and calls `npx skills add`. This is a read-only study; if a
  copy on disk is wanted, clone into its own empty directory under the agent-storage root and never
  execute from inside it.
- **Our six-stage shape already exists and is owner-ruled.** Relentless builds/proves/closes, the
  Designer argues, Operations takes alarms, FOUNDRY is retired (owner, by card 2026-11-02), and
  *"It's a builder/test-builder/judge pipeline, not an everything pipeline"* (owner, 2026-11-06).
  Any adoption must land inside that shape, not propose a parallel one.
- The twist in this item's name is the finding to check first, not a conclusion: their review skill
  opening a PR against itself may in practice be a daily no-op.

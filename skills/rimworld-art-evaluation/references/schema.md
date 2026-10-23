# Schemas

## Spec (input to `cards.build_card` / `runner.py run --spec`)

```json
{"subject": "RM_Ssurr", "label": "Ssurr", "template": "creature", "module": "walker",
 "candidate": "B", "provenance": "render 2026-09-24 · weepingstones2_ssurr", "artpipe_job": "<job id or null>",
 "description": "<def text>", "tier": "RM_", "invented": true, "earth_body_named": false, "body_plan": null,
 "departures": ["<visible feature>"], "canon": {"must_show": [], "engine_limits": []}, "owner_notes": [],
 "owner_kept": false, "depends_on": null, "previous_prompt": null, "size": {"drawSize": [1.4, 1.4]},
 "ports": ["<machines: each code-defined port, e.g. 'south facing: east side, hose'>"],
 "images": {"south": "<png>", "east": "<png>", "north": "<png>", "scale": "<true-scale panel png>",
            "living_reference": {"south": "<png>"}, "siblings": ["<png>"], "flight": [], "variants": [],
            "assembled": ["<in-game capture png>"], "wall_context": "<wall-mounted: each facing composed against its wall>"}}
```

Modules: creature `walker | pack | swimmer | amphibious | flyer | catch`; plant `ground_cover | bush | tree |
special`; machine `machine | part | hose | coupler | reel | tank | pump | wall_mounted` (wall_mounted needs
`wall_context`; the ladder and reel misses of 2026-10-23 are criteria ledger CL-004/CL-005). Departures/earth_body_named/body_plan
come from `infrastructure/state/art_eval/briefs/<def>.json` when the spec has none (`runner.py brief`).
⛔ `owner_notes` are his notes from OTHER sittings or standing ones — never the verdict the subject is being
scored against.

## Card (`card.json` in the card directory)

The spec minus images, plus `panels {name: file}`, `image_sha256 {file: sha}` (the card copies, ≤ 2000 px),
`source_sha256 {panel: sha}` (the judged originals — what the shadow sheet must show), `gates`
(`visible_height_px` at alpha > 16, `height_spread` and its 15 % flag, `duplicates`, `alpha`) and `card_sha`.

## Opus reply — `rm-art-eval/opus@v1`

`observed {image: text}`, `nearest_earth_animal`, `checklist {ITEM_ID: {status ok|fail|unreadable|n/a, seen}}`
(every applicable item), `findings [{code, where, seen, quote, confidence 0–1, model_severity, fix}]`,
`overall good|weak|really_bad`, `needs_call_why`, `proposals`. Validated by `policy.validate_opus`; one re-ask,
then HOLD_ERROR.

## GPT reply — `rm-art-eval/gpt@v1`

`image_seen`, `concerns [{id K1.., answer confirmed|refuted|unclear, evidence}]`, `findings [...]`,
`verdict strong_accept|regen|unsure`. Validated by `policy.validate_gpt`.

## Regen request — `rm-art-eval/regen@v1`

`edits [{finding, change}]`, `invariants [...]`, `reference keep|none`, `prompt`, `by model|deterministic`.
`runner.regen_jobs` turns each into a `fill_queue.py` row (`id arteval_<def>_r<round>`, `target_def`,
`rimflow_item_id`, `prompt`, `facings`, `style_notes`, priority 40).

## Decision record (`infrastructure/state/art_eval/runs/<run>/decisions.jsonl`)

`subject, candidate, template, module, at, card_sha, image_sha256, source_sha256, artpipe_job, gates,
prompt_versions {preamble, opus_first_pass, gpt_targeted_second_look, regen_prompt_edit, departures_brief, template,
severity: {tag, sha}}, models {opus: [{model_requested, models_reported, seconds, cost_usd}], gpt: [...],
regen: {...}}, opus {band, reply, detail {blocking, polish, gross, incomplete, model_overall,
severity_disagreements}}, gpt {concerns, reply, detail, outcome} | null, regen {findings, request} | null,
decision, round, reasons [...], seconds`. `run.json` beside it: `run_id, test, started, subjects, versions_key`.

## Shadow log (`shadow_log.jsonl`) and criteria ledger (`criteria_ledger.jsonl`)

Shadow: `at, run, subject, template, pipeline_decision, owner_answer keep|should_accept|should_regen|other,
override, blocking, note[, ledger]`. Ledger: see `criteria_ledger.md`.

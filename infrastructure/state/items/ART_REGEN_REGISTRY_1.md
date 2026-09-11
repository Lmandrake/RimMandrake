# ART_REGEN_REGISTRY_1 — the tracking layer above the art queue

Design (ruled by owner card, 2026-09-11):
`design/RimMandrake/art_regen_registry_design.md`. The rulings: one CLI owns
every write; done = committed to repo; retry cap 3 then park+escalate;
dashboard rides the hub artifact (DASHBOARD_HUB_ARTIFACT_1).

## spec
- `src/RimMandrake/Utils/artpipe/artreg.py`: sole writer of
  `infrastructure/artpipe/registry.jsonl` (append-only events; schema in the
  design doc §1). Subcommands: register / queued / generated / validated /
  sheeted / verdict / committed / deployed / backfill / render / status.
- Target vs job identity per design §1; `repurposed` verdict closes
  `as_target` AND re-registers the original with source "repurpose of <job>".
- Spend views join `throughput.jsonl` on job_id — %weekly window, $ at plan
  rate (5% ≈ $1), Gemini `cost_usd` additive, cost per ACCEPTED image. All
  relayed MEASURED/UNMEASURED, never bare.
- `render`: burn-up (scope line with labeled steps vs committed line), state
  counts, iterations histogram, parked-at-cap list, projection of current
  scope at measured velocity → repo HTML + the hub's `art_status.json`
  (generatedAt + source fingerprint).
- `backfill` seeds from existing throughput.jsonl + done/failed manifests;
  retroactive targets get source: backfill.
- Daemon/fill_queue integration: fill_queue.py emits `registered`+`queued`;
  artpiped.py emits `generated`+`validated` through the CLI.

## verify
- [ ] A full lifecycle (register → queue → generate → validate → sheet →
      reject×1 with notes → requeue → accept → commit) shows correctly in
      `artreg.py status` with iteration count 2 and joined spend.
- [ ] A `repurposed` verdict closes the as-target and re-registers the
      original; both visible in status.
- [ ] 4th rejection parks the target and it appears on the escalation list.
- [ ] Backfill runs on the live throughput.jsonl (93+ rows) without error;
      counts relayed MEASURED.

## criteria
The owner can ask "how many targets, how many done, what did an accepted
image cost this week" and the art tab answers all three with MEASURED numbers;
a new verdict sheet adding targets moves the scope line as a labeled step.

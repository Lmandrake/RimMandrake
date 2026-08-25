## spec
`research/Multimodel_architecture_analysis.md` measured that **every census, sweep and existence
check in this project's history ran on Opus**: there is no `.claude/agents/`, no `model` key in any
settings file, and the repo's one model-selection line — `skills/efficient-subagents/SKILL.md:52`,
`model: haiku` for greps — had never been executed.

`infrastructure/agents/Agent_Policy.md` replaces that with one question: **if this goes wrong, who
catches it?** Compiler/validator → haiku. Another agent → sonnet. Nobody → opus. Only the owner's
eye → opus, and it goes to him. Tier follows *detectability of error*, not perceived difficulty,
because our failures are not bad code — they are plausible answers nobody disbelieved.

Wired into `POLICY.md` § Model choice, `CLAUDE.md:3` (so it loads every session, every seat), the
four seat files' new `## Model` sections, `efficient-subagents`, `agent-fanout-research`, and
`.claude/hooks/block_agent_without_model.py`.

Trimmed in the same pass, on the owner's instruction:
- **`say.py` deleted.** It wrote `status/<SEAT>.json` for the board's CURRENTLY panel, which was
  removed 2026-08-22 — `status_server.py:228` and `status_board.html:221` carry the tombstones, and
  `status/` held only `game.json`. Four seats were being told to write files nothing read.
  Superseded by `rimflow seat --note`, which lands on the ledger the board does read.
  `STRUCTURE.md` and `LOAD_PROCEDURE.md` repointed.
- **The no-messaging ruling** was restated in full in DECIDE/BUILD/CHECK — three hand-kept copies of
  a rule already in `CLAUDE.md` and `POLICY.md` and enforced by a hook. Collapsed to REP's
  two-line pointer form.

Net **−50 lines** across the doctrine tree while adding a policy.

## verify
- `python3 .claude/hooks/selftest_block_agent_without_model.py` → 13/13, exit 0.
- An `Agent` call with no `model` and a generic `subagent_type` is denied; `fork` and named agent
  types pass (they carry their own model, so gating them would be a false block).
- `grep -rn "say\.py"` over `*.md`/`*.py` returns only the two tombstones and the historical
  `infrastructure/output/audit_2026-08-20_*` files.
- `.claude/settings.json` parses and carries 5 `PreToolUse` entries.

## criteria
No seat can spawn a subagent at an unstated tier. `Agent_Policy.md` is reachable from the first
line of `CLAUDE.md`, so it loads before any seat acts. No directive anywhere still points at a
file or panel nothing reads.

## watch out
⚠️ **The routing table is judgment, not measurement.** Tier profiles and prices are CONFIRMED; which
work belongs at which tier is a considered opinion and is wrong somewhere. The ledger already
records who closed what and pass/partial/fail (81/66/12) — stamp `model=<tier>` in the `close` note
and it answers accepted-work rate per model with no new tooling. **Revise the policy from that, not
from argument.**

⚠️ **The guard fails open** on unparseable stdin, deliberately: a hook that breaks subagent spawning
across four windows is worse than the habit it prevents. Its real risk is the false block, which is
why `fork` and named agent types are exempt and why the selftest leads with those cases.

⚠️ Prices are Anthropic **API list** as a ratio. We are on Max; subscription weighting per model is
UNMEASURED. Do not quote a dollar saving.

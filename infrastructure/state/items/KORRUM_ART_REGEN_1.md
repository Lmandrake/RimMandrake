# KORRUM_ART_REGEN_1 — the korrum renders from the donor's own texture

## the ruling

**Owner, 2026-09-22**, sheet note on the korrum row of the identity picker:
*"This is good for Scarlands. Regenerate art."*

## what is wrong — MEASURED 2026-09-22

`RSW_Korrum` (our port of Alpha Animals' `AA_BoulderMit`, renamed from `RSW_Stoneback` at
`4b068ea5d`) has **no art of ours at all**. Its `texPath` is
`Things/Pawn/Animal/AA_BoulderMit/AA_BoulderMit` — the **donor's** path, served only by
`sarg.alphaanimals`. Nothing under `src/` matches it (searched the whole tree).

⛔ That violates its own port batch's ruling. `DESERT_FAMILY_PORT_EXECUTION_1` carries the
owner's 2026-09-20 words: *"All of the desert sheet should be keep but replace with our own
version of creature and art. Port. All of them. Now."* The def half was done; the art half
was not, and nothing tracked it — this creature is **not** in
`DESERT_PORT_PLACEHOLDER_ART_1`'s 13-species pending list either.

## already queued — do NOT file new jobs

Per the standing rule to check for existing art before queuing more, this was checked first.
**Three jobs already exist** and were re-keyed by `STONEBACK_DEFNAME_COLLISION_1`:

`infrastructure/artpipe/pending/RSW_Korrum_{south,east,north}.json` — priority 150,
512×512, drawsize 3.5, created 2026-09-20T16:51:43Z. Their prompt already describes this
creature: *"A massive crab-like creature carrying a huge boulder-textured shell on its back,
thick stony grey-brown hide, slow and ancient looking, Star Wars alien creature design,
desert palette, painterly game-art style."*

🔴 They were filed as `RSW_Stoneback_*`, i.e. under the **bokka's** defName. Landing them unchanged
would have delivered korrum art onto the bokka. They are now correctly keyed.

⛔ **The old wording here said the bokka "already has finished art" — that was FALSE** and is
corrected rather than annotated. MEASURED 2026-09-23: the bokka's three PNGs are Biomes! Caverns'
**stone-mimic** art (a legless mound with one dot eye) against a def whose body is
`QuadrupedAnimalWithClawsTailAndJowl` with left/right claw tools. Its own regen is queued under
`STONEBACK_BOKKA_ART_STANDARD_1`. ⇒ The collision was real and the re-key was right; only the
reassurance about the other creature was wrong.

⚠️ **The re-key renamed the job FILES but wrote no registry event**, so `registry.jsonl` still
records these three as `RSW_Stoneback/*`. ⇒ A name search for the bokka's art finds them and reads
as "already queued" — a false positive that cost a search. Disambiguate on `ts`
(`2026-09-20T16:51:43Z`) and `source` (`DESERT_FAMILY_PORT_EXECUTION_1`, the korrum's batch).

## ✅ status 2026-09-23 — BLOCKED, not neglected. No decision is owed.

⚠️ The artpipe daemon is **quota-blocked until ~2026-09-26T19:52 UTC** (FOUNDRY measured this
from `throughput.jsonl`'s own `secondary_resets_at`, not guessed) — **and it does not run on the Mac
at all**, so this cannot advance from the laptop under any circumstances.

🔑 **This is why the item has ridden several handoffs untouched, and that is correct behaviour.**
⛔ Do not carry it forward as a pending decision or keep re-asking whether to drop it: its next
action is mechanical and belongs to whichever Desktop session follows the quota reset. Re-checked
2026-09-23 — the three jobs are still in `pending/`, still correctly keyed, nothing to do.

## spec

1. When the daemon clears, confirm `infrastructure/artpipe/done/` (and `registry.jsonl`)
   carry `generated`/`validated` events for the three `RSW_Korrum_*` jobs.
2. Land the art into `src/RimStarWars/SWBestiary/Textures/` under **our own** namespaced path,
   matching the sibling convention (`swanimals/...`), never the donor's path.
3. Repoint `RSW_Korrum`'s `texPath`, its `bodyGraphicData` and **all three `lifeStages`
   entries** (drawSizes 1.5 / 2.7 / and the third — read them, do not assume) in
   `src/RimStarWars/SWBestiary/Defs/DesertPort/RSW_DesertPortMisc_Races.xml`.
4. `validate_patch.py --defs …` on that file, then deploy and look at it in-game.

## verify

No `texPath` on `RSW_Korrum` references `AA_BoulderMit` or any donor path; the three facings
resolve under our own Textures tree; the creature renders at all three life stages.

## criteria

The korrum is ours — def and pixels — so the mod does not need Alpha Animals installed to
show its own animal.

## FOUNDRY, 2026-09-24: title's "quota-blocked to ~2026-09-26" is now stale

All 3 jobs are still in `infrastructure/artpipe/failed/`, but the latest manifest's
failure reason is `worker_error` / "no image produced after 4s (exit 1)" with no
`primary_resets_at`/`secondary_resets_at` timestamp — not a quota block. This matches
a live Codex-channel outage (websocket 403 Forbidden) affecting the whole daemon this
session (see `CANON_CREATURE_REGEN_1` wave 4 and `DESERT_PORT_PLACEHOLDER_ART_1`'s
2026-09-24 notes). The item's own title still says "quota-blocked to ~2026-09-26" —
that was true of an earlier attempt, is no longer the live blocker, and needs
correcting the next time this item's title is touched. Not requeued this pass
(nothing to gain while the channel itself is down); no action taken beyond this note.

## FOUNDRY, 2026-09-24 (same session, later): live def check — RSW_Korrum does NOT resolve yet

Checked opportunistically while verifying other names for `ROSTER_DEAD_BMT_NAMES_SWEEP_1`
(this Desktop session has live bridge access). `jawa/get_defs` on `ThingDef/RSW_Korrum`
and `PawnKindDef/RSW_Korrum` both came back **MISSING** on the currently-running
process, despite `mandrake.rsw.swbestiary` being active in `ModsConfig.xml` and the
def genuinely present in `src/RimStarWars/SWBestiary/Defs/DesertPort/
RSW_DesertPortMisc_Races.xml` (confirmed on disk). Not chased further this pass — the
most likely explanation is simply that defs parse once at startup and this def wasn't
deployed yet as of the current process's launch, same as every other def-only change
this session waiting on a restart. Flagging rather than asserting: if a restart
happens and `RSW_Korrum` is STILL missing afterward, that would be a real defect
worth its own investigation, not assumed here.

## FOUNDRY, 2026-09-24 (BELT art slot): channel recovered, all 3 art jobs GENERATED

The "no image produced ... exit 1" failures across the whole daemon batch (this item's
note above, `bluedesert_*`, `rsw_zakkro_*`, etc.) were re-checked against their own
`worker_stderr_tail`, not assumed: every one carries `ERROR: You've hit your usage
limit ... try again at Sep 24th, 2026 12:23 AM` — a genuine Codex quota exhaustion
(local/Pacific time, matching the rollout-path timestamps), **not** the websocket 403
outage this item's previous note guessed at. By the time this pass started (2026-09-24
~06:02 Pacific / 13:02 UTC) that reset time was ~5.5 hours in the past.

Ran `requeue_quota_failures.py` (the tool built for exactly this — moves any
`failed/*.manifest.json` carrying the quota sentence back to `pending/`): 168 jobs
requeued, including all three `RSW_Korrum_{south,east,north}`. Bumped the three
Korrum jobs' `priority` from 150 to 1 so they claimed ahead of ~140 other
priority-100 jobs. **All three landed in `done/` with `status: ok`,
`worker_status: ok`** — confirmed by reading each `.manifest.json` directly, not
inferred. 16 of the first ~20 requeued jobs resolved within the observation window,
0 new failures. **Channel is healthy as of this session.**

Two `artpiped.py` processes were found running (PIDs from ~09:22 and ~21:11 the
previous day) — checked via `/proc/<pid>/fd`, not killed: they hold **disjoint**
worker-slot leases (w0/w1/w2 vs w3/w4/w5), so this is two independent worker pools
sharing the queue, not a stuck duplicate. Left both running.

Next step per this item's own spec: land the three generated PNGs into
`src/RimStarWars/SWBestiary/Textures/` under our own namespaced path and repoint
`RSW_Korrum`'s `texPath`/`bodyGraphicData`/all three `lifeStages` entries — not done
this pass (art-regen slot only, no def/texture wiring).

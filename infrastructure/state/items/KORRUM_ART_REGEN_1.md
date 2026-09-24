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

## FOUNDRY, 2026-09-24 (no bridge): art landed, def repointed, offline-validated, deployed — verify owed to bridge holder

Confirmed all three `infrastructure/artpipe/done/RSW_Korrum_{south,east,north}.manifest.json`
carry `status: ok` / `worker_status: ok` (read directly, not inferred). Their
`worker_self_report.out` paths pointed at
`infrastructure/artpipe/_artsrc/RSW_Korrum_{south,east,north}/RSW_Korrum_{...}.png`.

Copied those three PNGs into
`src/RimStarWars/SWBestiary/Textures/swanimals/Korrum/Korrum_{south,east,north}.png` —
matching the sibling convention read straight off `RSW_GraniteSlug.xml`
(`<texPath>swanimals/GraniteSlug/GraniteSlug</texPath>`, files
`GraniteSlug_{south,east,north}.png` in the matching folder).

Repointed all three `lifeStages` `bodyGraphicData/texPath` entries in
`src/RimStarWars/SWBestiary/Defs/DesertPort/RSW_DesertPortMisc_Races.xml` from
`Things/Pawn/Animal/AA_BoulderMit/AA_BoulderMit` to `swanimals/Korrum/Korrum`,
drawSizes unchanged (1.5 / 2.7 / 3.5 — this ThingDef/PawnKindDef carries no
separate top-level `texPath`; all three donor references were inside these
`lifeStages` blocks). No `AA_BoulderMit` reference remains anywhere in that file
except inside provenance-comment prose (donor-mapping notes, not live paths).

`validate_patch.py --defs <Data> --defs <Workshop 294100> --defs <Mods>` on the
whole file: **0 errors, 3 warnings** — all three warnings are on `RSW_Ashworm`
(a different creature in the same file, its own pre-existing donor-path issue,
untouched this pass). Korrum's new texPath drew no warning.

`deploy_custom_mods.py --mod SWBestiary` plan showed exactly the expected diff
(3 new PNGs `+`, the def file `~`, plus pre-existing unrelated in-game-not-in-repo
drift on three other DesertPort body files that this pass did not touch or
prune) — `--apply` deployed 4 files, verified in sync.

**Not done, no bridge this pass:** no live render check. `needs: bridge` is
already the item's state — the next bridge holder should restart (defs parse
once at load) and confirm the korrum renders at all three life stages
in-game, per this item's own `## verify`. Also re-check at that restart
whether `RSW_Korrum` now resolves via `jawa/get_defs` (the 2026-09-24 note
above flagged it MISSING pre-restart, most likely just parse timing).

Not closed: `## criteria` requires def AND pixels AND live-rendering proof: the
first two are now true, the third is still owed. Left `doing`.

## FOUNDRY, 2026-09-24 (later, live): defs now resolve live — MEASURED, not the flagged-MISSING state; still no render proof

Fresh 621-mod session (post-restart from an earlier session), `jawa/get_defs`
on both `ThingDef/RSW_Korrum` and `PawnKindDef/RSW_Korrum`: **both resolve**
(`found: true`), confirming the 2026-09-24 note above ("does NOT resolve
yet... most likely just parse timing") was correctly diagnosed as a
pre-restart artefact, not a real defect — a restart did fix it, as that note
predicted. `ThingDef/RSW_Korrum` reads `modName: "RimMandrake: SW · Bestiary"`,
`packageId: mandrake.rsw.swbestiary`, confirming the deploy from the prior
pass is live.

**Still not closed**: no map/render check was reached this pass.
`rimworld/start_debug_game_ready` (a quicktest, chosen to avoid the canonical
save's live-combat starting state — see `BACTA_TANK_CORE_1`'s note this same
session for the full account) crashed the shared game process on an
unrelated Vehicle Framework `NullReferenceException` in `Game.Dispose()`
before any spawn/screenshot was attempted. The process is wedged with no
bridge-reachable map or load route afterward — pure `DefDatabase` reads
(`jawa/get_defs`) still answer, which is how the confirmation above was even
possible, but `jawa/spawn_pawn` + `take_screenshot` need a live map and none
is reachable this session. Needs a restart (not this pass's call) before the
render half of `## verify`/`## criteria` can be attempted. Left `doing`.

## FOUNDRY, 2026-09-24 (live test v2, post-restart): render CONFIRMED live — closing

Fresh restart (orchestrating window), canonical save loaded via `rimworld/load_game`
(621 mods, compatible, 0 missing). Confirmed `ThingDef/RSW_Korrum` and
`PawnKindDef/RSW_Korrum` both resolve via `jawa/get_defs` on this fresh process too.

Spawned `RSW_Korrum` twice via `jawa/spawn_pawn` (once far from the colony at
230,230 — rendered but fully FoW-shaded, a `references/map-authoring.md` "fog
defeats screenshots" case, not usable for judging art; once at 190,140, near the
colony's own explored/lit area, faction `None` — this one rendered clean) and
screenshotted both (`Transient/` scratch, not committed — screenshots are
ephemeral evidence here, not deliverables). The second shot shows a real,
distinct, non-donor sprite: a massive crab-like creature with a rounded
boulder-textured shell on its back and jointed clawed legs, rendered in a
stony grey-brown palette — matching the queued art prompt
("massive crab-like creature carrying a huge boulder-textured shell... thick
stony grey-brown hide") exactly, and visibly nothing like Alpha Animals'
`AA_BoulderMit` donor texture (no magenta, no placeholder, no donor art).
Both test pawns destroyed cleanly afterward (`Actions\T: Destroy` by cell,
each cell held only the korrum, `thingCount: 0` confirmed after).

`## verify`'s three conditions are now all met: no `texPath` on `RSW_Korrum`
references `AA_BoulderMit` (confirmed prior pass, re-confirmed this pass — the
live def's `modName`/`packageId` show our own `mandrake.rsw.swbestiary`, not a
donor mod), the three facings resolve under our own `swanimals/Korrum/` tree
(prior pass), and the creature renders — now MEASURED live, not just deployed.
`## criteria` ("the korrum is ours — def and pixels — so the mod does not need
Alpha Animals installed to show its own animal") is met.

Closing. `git rev-parse HEAD` at close: `9b64f4fded6ecba29145ab60035e1517085df440`.

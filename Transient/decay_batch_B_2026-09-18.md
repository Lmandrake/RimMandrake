# Queue Decay Verification — Batch B — 2026-09-18

## COLONY_VISIBILITY_BUILD_1

Wants: raid-threat-scaling Colony Visibility dial; no real blocker left, actively being live-tested.

**Verdict: LIVE** — CONFIRMED

EVIDENCE:
- ledger `2026-09-18T12:02:09Z` bridge taken "re-confirm threat-point Prefix live" (same day as this audit)
- `infrastructure/state/items/COLONY_VISIBILITY_BUILD_1.md:92-104` — md5sum confirms deployed DLL byte-identical to HEAD build
- `infrastructure/state/items/COLONY_VISIBILITY_BUILD_1.md:120-146` — real bridge limitation: `Dialog_DebugOptionListLister` picker rows don't complete via click

Action: no intervention needed; fix `DebugActions_Visibility.SetVisibility` picker dependency, or accept 09-13 live proof as standing evidence.

## WEAPONS_DONOR_RETIREMENT_1

Wants: all 6 weapon donor packs retired; 5/6 done, sole remaining is `guy762.mm.kotorcore`, blocked (2026-09-07) on "parked DROID_SYSTEM_BUILD_1"/`DROID_DONOR_PATCH_GATE_1`.

**Verdict: STALE_BLOCKER** — CONFIRMED

EVIDENCE:
- ledger: `DROID_SYSTEM_BUILD_1` closed `5736f2888e2` at `2026-09-12T12:43:14Z` — no longer parked
- ledger: `DROID_RETIRE_KOTORDROIDS_1` closed `2026-09-10T08:42:57Z` "guy762.kotordroids was retired tonight" — the inheritance hazard cited is now moot
- `src/RimStarWars/Armoury/About/About.xml:44` declares `guy762.mm.kotorcore` as a hard `modDependency` (added 2026-09-02 by `ARMOURY_ABSORBED_FRAMEWORK_DEPS_1`) — a possible NEW undiscussed reason it can't simply retire

Action: reclaim and re-verify — cited blocker chain has dissolved, but check whether the About.xml dependency is load-bearing before forcing kotorcore's retirement.

## RIVER_STEAM_ANIMATION_1

Wants: animated steam flecks on Pyrelands rivers; mechanism built and deployed, live-observe proof blocked by a genuine bridge tooling gap, not a stale premise.

**Verdict: LIVE** — CONFIRMED

EVIDENCE:
- `infrastructure/state/items/RIVER_STEAM_ANIMATION_1.md:118-136` — real authored Pyrelands river confirmed live at 9 tiles, terrain-verified
- `infrastructure/state/items/RIVER_STEAM_ANIMATION_1.md:138-149` — "newly-identified bridge rendering gap... debug-generated maps render as blank void"; documented in `skills/rimbridge/references/traps.md`
- ledger `2026-09-13T06:39:43Z` bridge taken, left `doing`

Action: next session either works around the render-void trap or waits for a human-observed session near a live Pyrelands river tile in the actual campaign.

## COLD_LOAD_RUN_SHEET_4

Wants: running run-sheet accumulating "readings that could not be taken offline" entries across sessions, each owed a live-load verification.

**Verdict: LIVE** — CONFIRMED

EVIDENCE:
- `infrastructure/state/items/COLD_LOAD_RUN_SHEET_4.md:98` — "Leaving `doing` -- three of six entries (2b, 3, 4's full form) still owed."
- git `77b83b31c` "COLD_LOAD_RUN_SHEET_4: fold in ENTRY 7 (Giddy-Up null-key + duplicate-key restart verify)"
- ledger `2026-09-18T02:32:36Z` note folding ROT_SPORECLOUD_PORT_1 in "as owed entries rather than restart mid-wave"

Action: no action — active, correctly-open accumulator item; keep working entries as loads happen.

## RAIN_BAN_SCOPE_DRIFTED_1

Wants: owner ruling on whether the 2026-08-21 rain-ban (zero rain, hilliness<4) still applies world-wide now the selector spans 17 biomes (not just AB_FeraliskInfestedJungle as when ruled). Blocker: genuinely for the OWNER.

**Verdict: NEEDS_OWNER** — CONFIRMED

EVIDENCE:
- `infrastructure/state/items/RAIN_BAN_SCOPE_DRIFTED_1.md:27-31` — "does the rain ban still apply to the WIDER set... or does the ban now need re-scoping"
- ledger file event `ts:2026-09-08T05:16:23Z`, only 3 ledger hits total, no close/owner-ruling event since
- `git log --grep RAIN_BAN` shows only the filing commit `a1653e029`; the 2026-09-18 worldmap-pass rulings (`f082d783e`, rulings 2-9) don't mention the rain ban

Action: still awaits an owner card; escalate at next owner sitting — nothing to close or reopen.

## ASHKARR_NIGHTSIDE_LAYER_SUPERSEDED_1

Wants: owner ruling — is "no AB_RockyCrags tile above freezing" still standing, and if so what should above-freezing RockyCrags convert to now both original carve targets (HorrorWastes, BMT_CrystalCaverns) are dead/banned. Live data at filing showed RockyCrags at 1,984 tiles up to +15°C.

**Verdict: NEEDS_OWNER** — CONFIRMED

EVIDENCE:
- `infrastructure/state/items/ASHKARR_NIGHTSIDE_LAYER_SUPERSEDED_1.md:29-31` — "is the... ruling still standing... what should above-freezing RockyCrags convert TO"
- ledger file event `ts:2026-09-08T05:25:24Z`, only 3 ledger hits, no closing/ruling event
- `design/Jawa/worldbuilding/biomes/forsaken_crags.md` (now the ratified AB_RockyCrags/nightside sheet under `BIOME_FREEZE_FABLE_REVIEW_1`) does not mention an "above freezing" ruling; 2026-09-18 worldmap-pass rulings 6-9 don't touch this either

Action: still genuinely open; `forsaken_crags.md` is the right place to fold the eventual answer, but nothing has ruled on it yet.

## BIOME_LANDMARK_REFINEMENT_1

Wants: per-biome curation of BENCH-drafted landmark density on 8 dense biomes (Greentide/Contagion/Webwork/Weeping Stones/Slime/Scarlands/Pyrelands/Cracked Lands); filed `for:OWNER`.

**Verdict: NEEDS_OWNER** — CONFIRMED

EVIDENCE:
- ledger `ts:2026-09-08T14:36:48Z` `file` event, only 1 ledger hit total, no claim/close since
- `infrastructure/state/items/BENCH_REBOOT_HANDOFF_202609081448.md:28,48,98` still lists it as owed, unstarted
- `git log --grep`/biome-name search across commits since 2026-09-08 shows no landmark-density curation pass on these 8 biomes (only naming/count work under `LANDMARK_NAMING_PASS_1`/`WORLDMAP_FINAL_REVIEW_1`, a different concern)

Action: still genuinely open, awaiting an owner decision — surface at next sitting; no item file exists (never filed past the ledger `file` event), only the ledger line and handoff-doc mentions.

## MOD_CONSOLIDATION_SPRINT_1

Wants: mechanical 77→53 mod consolidation (git mv/About merges/re-prefix/ModsConfig swap) per the signed-off plan; gated on 3 named items.

**Verdict: DONE_UNRECORDED** — CONFIRMED

EVIDENCE:
- `infrastructure/state/items/MOD_CONSOLIDATION_SPRINT_1.md:92-102` — "Second full load: UP in ~17 min, 590 active, zero texture errors... Runbook CLOSED"
- Live `ModsConfig.xml` (636 mods, read via `/mnt/c/.../Config/ModsConfig.xml`): all 14 dying packageIds from the item's swap table (`mandrake.rut.factionslate`, `mandrake.rsw.beastnorm`, etc.) are absent — confirms the swap landed live
- All 3 named gates closed: `CHRONICLE_EVENT_SPINE_1` (sha `2502b401`), `GRAFFITI_GENERIC_MARKS_1` (sha `b9ac45cb`), `PYRELANDS_GENERIC_TEXT_1` (sha `a3e5ba3d`) — but ledger has only `file`(2026-09-08T23:34:56Z) + a refused `claim` for this ID itself, never a `close`

Action: rimflow-close this item (parent to action) — work is fully landed and live-proven, just never recorded closed.

## IKEE_MYNOCK_ART_REGEN_1

Wants: regen custom art for Ikee (owner REJECTED, keep donor) and Mynock (owner approved) via Codex pipeline. Stated blocker: a live UAC dialog froze the owner's screen mid-background-run on the shared Codex home; item paused "AFK" mid-session.

**Verdict: DONE_UNRECORDED** — CONFIRMED

EVIDENCE:
- ledger `ts:2026-09-09T05:08:04Z` note — "Mynock all 3 facings (south/east/north) generated, validated (PASS...), and shipped via new mod mandrake.rsw.mynockart"; `ts:2026-09-09T05:10:06Z` `unblock` — "owner present tonight, not AFK - stale block no longer applies"
- `Transient/art_gen/mynock/` holds all 3 facings' `*_final.png` outputs (south/east/north v2), dated Sep 10
- Live `ModsConfig.xml`: `mandrake.rsw.mynockartoverride` present and active; ledger `ts:2026-09-12T06:27:21Z` "Ikee half is DEAD per earlier owner ruling — don't resume"
- No `close` event for this ID in the ledger despite both halves being resolved (Ikee cancelled, Mynock shipped+live)

Action: rimflow-close this item — both halves resolved (Ikee cancelled by owner ruling, Mynock generated/validated/shipped/live); the UAC blocker was already lifted same-session once the owner returned.

## KOTOR_CRYSTAL_GENSTEP_DRIFT_1

Wants: fix live KOTOR_CrystalFormation genstep scattering only Stygium (repo's absorbed copy lists 11-12 variants ungated). Stated blocker: repo fix is under an active DEPLOY_HOLD because donor `guy762.mm.kotorcore` is still active in ModsConfig (redeploying now would duplicate defNames).

**Verdict: LIVE** — CONFIRMED (blocker still holds, correctly)

EVIDENCE:
- ledger `ts:2026-09-09T18:57:36Z` `block` — "Redeploying now would create a duplicate KOTOR_CrystalFormation defName against the still-active donor... blocked on DROID_DONOR_PATCH_GATE_1"
- `src/DEPLOY_HOLD.txt:172` still lists `Armoury/Defs/Absorbed_KotorCore/*` held "donor guy762.mm.kotorcore still active"
- Live `ModsConfig.xml` (read directly, 636 mods): `guy762.mm.kotorcore` IS present — the stated blocker is confirmed still true today, not stale
- Related gates `DROID_DONOR_PATCH_GATE_1`, `DROID_KOTORDROIDS_PORT_WAVE1_1`, `DROID_SYSTEM_BUILD_1` are all closed, but none of them retires the donor itself

Action: no action — correctly blocked; only closes when `guy762.mm.kotorcore` actually retires from the live mod list (tracked elsewhere, not this item's job).

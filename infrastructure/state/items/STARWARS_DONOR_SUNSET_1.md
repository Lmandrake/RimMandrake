# STARWARS_DONOR_SUNSET_1 — retire the remaining third-party Star Wars donors

Owner, verbatim (2026-09-02): *"file this as a ticket to track to get rid of
them all so we don't forget. And I bet we can get rid of Mlie and TSDA very
quickly if we put our mind to it. And we should."*

This pass is SCOPING ONLY — a census and wave plan, cross-checked against the
existing `design/Jawa/sw_ownership_survey.md` (2026-08-30, per-mod measured
cards) and the live `ModsConfig.FULL.LATEST.xml` (593 mods). **Nothing has
been retired, ModsConfig is untouched.** Per this project's own incident
history (`WEAPONS_DONOR_RETIREMENT_1`'s 2026-08-31 incident: a donor
retirement broke the owner's live game because a dependent mod outside the
item's own stated scope wasn't checked) — every mod below was checked against
the WHOLE active list, not just against each other.

## spec — the real candidate set (not exactly 12; see note below)

Already retired earlier tonight/this week, NOT in scope here: `guy762.kotorweapons`,
`maincrep.eweb`, `rpgwanderer.opturret`, `m3.continued.jangodsoul.starwars.bti`
(JDS Armory), `sov.sith` — all confirmed absent from the live 593-mod list.

**⚠️ Count note**: the owner said "12 mods." The actual set of active,
genuinely Star-Wars-themed third-party mods measured against the survey and
the live list comes to **14**, plus 2 structurally-coupled utility mods that
aren't themselves Star-Wars-branded (the leutiankane mines patches) and one
borderline framework mod (`jecrell.jecstools`) that the survey itself flags as
"not genuinely SW." Rather than force a match to 12 by guessing which 2 he
wasn't counting, every mod is listed below with its real complexity — his
call which subset the ticket tracks.

| mod | defs/C# | our-touch | verdict this pass |
|---|---|---|---|
| `m3.continued.jangodsoul.starwars.tsda` (TSDA) | 59 defs, 0 C#, 0 rev-deps | none found | ✅ **matches the owner's bet — genuinely quick.** Declares a dead `modDependencies` on the already-retired JDS Armory (harmless, RimWorld doesn't hard-fail on it) |
| `starwars.themedsounds` | 0 own defs (1 patch file re-pointing vanilla `SoundDef` clip paths) | metadata only | ✅ **quick** — nothing of its own to preserve; retiring just reverts to vanilla stock sounds |
| `lumi.swlights` | 3 ThingDefs, 0 C# | metadata only | ✅ **quick** — trivial, world-save presence 10 total |
| `mlie.starwarsanimalcollection` (Mlie) | **1,581 defs, 0 C#**, art packed in a 32-33 MB AssetBundle | 🔴 **survey's own words: "largest, most load-bearing touch found in this survey"** — 3 of our own patch files fix its assets directly, our fauna census CSVs/`animal_contact_sheet.py`/`extract_bundle.py` tooling depend on it, `required_mods.md` cites it ADOPTED for Bantha/Sarlacc resolution (~150 creature defs), defNames carry **no consistent mod prefix** (bare species names — `Bantha`, `Rancor`, `Wampa`...), substantial world-save presence (`Bantha`=210, `Rancor`=114, etc., scan-grade) | 🔴 **contradicts the owner's bet — NOT quick.** The prior survey's own conclusion was "keep upstream, absorb never-or-late." Retiring this means either porting ~150 creature defs into our own mod first (a real absorption project, not a delete) or losing that fauna content outright. Flagging this plainly rather than agreeing with the optimism — **his call, with the real cost now on the table.** |
| `lee.theforce.lightsaber` | — | — | 🔴 **CONFLICTS WITH AN EXISTING RULING.** `sw_ownership_survey.md`'s own Tier 2 section records: *"lee.theforce.lightsaber STAYS UPSTREAM (owner, 2026-08-30): peripheral to the scenario, outside the ingest plan."* This item's "get rid of them all" is newer but doesn't name lightsaber specifically. **Not retiring this without an explicit reconfirmation** that the 2026-08-30 ruling is superseded — see `deciding-and-superseding` skill: a sweeping instruction doesn't silently overrule a specific prior one. |
| `guy762.mm.kotorcore` | 1,235 defs, C# via ABF/SynCore refs | — | ⛔ blocked on `DROID_DONOR_PATCH_GATE_1` (11 ungated ABF/SynCore XML references) and `DROID_SYSTEM_BUILD_1`'s droid platform, unchanged from those items' own state |
| `guy762.kotordroids` | 44 kinds, 22 races, 0 C# | — | ⛔ this mod's own content IS `DROID_SYSTEM_BUILD_1`'s wave-1 port target (`droid_system_build_spec.md` §7) — "retiring" it means porting its 44 kinds onto Droidworks first, not deleting |
| `neronix17.outerrim.core` | 446 defs, C# source on disk | — | ⛔ 3,156 world-save hits, two structurally-unguarded hard dependents (`leutiankane.mineablesor`/`mines2patchouterrim` — no `PatchOperationFindMod` gate anywhere), Droid Depot/Empire ride it |
| `neronix17.outerrim.droiddepot` | — | — | ⛔ rides Core + is `DROID_SYSTEM_BUILD_1` wave-2 port territory |
| `neronix17.outerrim.galacticempire` | — | — | ⛔ the one addon with a genuine C#-level Harmony coupling into Core's settings class, plus wave-2 port territory. Also: campaign's own "Galactic Empire" faction is REUSED VANILLA `Empire`, not this mod (`galactic-empire-is-reskinned-vanilla` memory) — worth confirming this mod isn't load-bearing for that before any retirement |
| `neronix17.outerrim.furnitureanddecor` | — | — | cosmetic, zero deps per survey — but still gated on Core staying active until Core itself resolves, so not independently retirable yet |
| `neronix17.outerrim.rebelalliance` | — | — | survey: "kept-suppressed, scenario ref" — needs the actual scenario reference checked before retiring, not assumed dead |
| `lumi.doorsexpanded` | 41 defs, 0 C# | 🔴 **retirement blocker**: `src/RimMandrake/BlastDoorFrameAsyncFix/` is OUR OWN Harmony fix with a hard `modDependencies` on this exact packageId | ⛔ do not retire without either porting the fix or accepting the bug it addresses returns |
| `btd.gbp.shippack.kotor.vge` | UNCERTAIN — survey flags "0 defs — re-check owed before any call" | — | needs a fresh measurement before any wave assignment |
| `leutiankane.mineablesor` / `mines2patchouterrim` | — | — | not independently Star-Wars-branded, but structurally coupled to Core (see above) — track alongside Core's wave, not as standalone "SW donor" retirements |
| `jecrell.jecstools` | — | — | survey: "not genuinely SW" (a framework mod, cut-managed) — likely out of scope for THIS ticket's intent; flagged, not included in the wave count |

## Proposed waves (by real risk, not by the owner's guess)

1. **Wave 1 — genuinely quick, do these first, matches the owner's own instinct for 2 of 3**: `starwars.themedsounds`, `lumi.swlights`, `m3.continued.jangodsoul.starwars.tsda`. Zero rev-deps, zero our-touch beyond metadata, no C#. Safe to execute as its own small item once `btd.gbp.shippack.kotor.vge` is re-measured (cheap to fold in if it turns out equally trivial).
2. **Wave 2 — real absorption project, not a quick win**: `mlie.starwarsanimalcollection`. Needs either a defName-prefixing absorption of ~150+ actively-referenced creature defs (large, AssetBundle art extraction included) or an owner decision to accept losing that fauna content. Do not fold into Wave 1's "quick" framing.
3. **Wave 3 — entangled with `DROID_SYSTEM_BUILD_1`'s own port plan, sequence together, not standalone**: `guy762.mm.kotorcore`, `guy762.kotordroids`, `neronix17.outerrim.core` + its 3 addons (droiddepot/galacticempire/rebelalliance/furnitureanddecor) + the 2 leutiankane mine patches riding Core. This is the same droid-porting work `DROID_SYSTEM_BUILD_1`/`DROID_DONOR_PATCH_GATE_1` already own — this ticket should point at those, not duplicate a parallel plan.
4. **Wave 4 — needs an explicit owner call before any wave assignment**: `lee.theforce.lightsaber` (conflicts with the 2026-08-30 "stays upstream" ruling — needs reconfirmation, not a silent override) and `lumi.doorsexpanded` (blocked on porting our own `BlastDoorFrameAsyncFix` first, or accepting its bug returns).

## verify

Each wave gets its own item when executed, following `WEAPONS_DONOR_RETIREMENT_1`'s
established discipline: back up `ModsConfig.xml`, retire ONLY that wave's mods,
cold-load-verify clean, `harvest_log.py` baseline unchanged, before touching the
next wave. Never bundle waves 1 and 3 into one restart — different risk classes.

## criteria

- [x] Real candidate set named and measured (this pass) — 14 genuinely
      SW-branded mods + 2 structurally-coupled utility mods + 1 borderline
      framework mod, not exactly 12; the owner's count wasn't force-matched.
- [x] Every candidate checked against the WHOLE active list for dependents,
      not just this ticket's own scope (the `WEAPONS_DONOR_RETIREMENT_1`
      incident's exact failure mode).
- [x] 4 waves proposed, ordered by real risk.
- [ ] Wave 1 executed (genuinely ready — smallest scope, needs its own claim/item).
- [ ] Wave 2 scoped as its own absorption project (not started).
- [ ] Wave 3 folded into `DROID_SYSTEM_BUILD_1`/`DROID_DONOR_PATCH_GATE_1`'s
      existing plan rather than duplicated.
- [ ] Wave 4's two open questions put to the owner explicitly (lightsaber
      ruling reconfirmation, doorsexpanded fix-porting decision).

## Open questions for the owner

1. **Lightsaber**: your 2026-08-30 ruling said `lee.theforce.lightsaber` stays
   upstream, peripheral to the scenario. Does "get rid of them all" include
   this one now, or does that ruling still stand?
2. **Mlie (starwarsanimalcollection)**: this is NOT a quick win — it's the
   single most tooling-integrated mod in the whole survey (~150 creature defs
   our fauna census/art-fix tooling actively depends on, no consistent
   defName prefix, art locked in an AssetBundle). Worth doing as a real
   absorption project, or is losing that fauna roster acceptable to just cut it?
## Cross-finding from the sandworm/Krayt survey (BENCH, 2026-09-02)

The campaign's giant Krayt Dragon SHIPS IN `mlie.starwarsanimalcollection`
(fauna cast rows: animal_census.csv:484,535; BiomeCast_Ashkarr.xml:522,607),
and the owner ruled it "keep just as it is" (swt:krayt-leviathans) — so the
Mlie absorption wave MUST port the Krayt, it cannot lapse. ⭐ Subagent reports
the mod is MIT-licensed on GitHub (⚠️ verify the license file before relying):
if true, art and defs are legally portable, which cuts the Mlie absorption
cost from "regenerate ~150 sprites" to "port and rename". Survey:
research/Jawa/sandworm_krayt_survey_2026-09-02.md

## Mlie dependency census — MEASURED (BENCH subagent, 2026-09-02)

research/Jawa/mlie_dependency_census_2026-09-02.md: **135 of 160 creatures
must port** (133 wild-spawn on Ashkarr via BiomeCast_Ashkarr.xml + 2
load-bearing off-biome: Bantha as a faction pawnGroupMaker carrier, Fambaa
patched by RimStarWars/SeasWaterline). 25 drop free (24 blanket-sweep-only +
CorellianHound already MEASURED_DEAD). Confirms the scoping verdict: a real
absorption project, not a quick win — though the reported MIT license (verify)
means porting, not regenerating.

**Two owner calls needed before porting starts:**
1. `Nuna` is a defName COLLISION with vanilla Core; the dumped list resolves
   to Mlie's version — confirm which Nuna ships (stats/art differ).
2. Wampa and Acklay were cited in required_mods.md as adoption reasons but
   have NO functional wiring in the cast — design intent never landed;
   decide wire-them-in vs let-them-drop rather than silently losing them.

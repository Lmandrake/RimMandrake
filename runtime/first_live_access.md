# first_live_access.md — Day-One Runbook (running RimWorld + real mods + harmonized save)

_What to do the **first time** we have the live install, the real 1.6 mod list on disk, and a
saved game to point tools at. This is the tooling/agent integration runbook — the in-game
scenario decisions live in `setup_checklist.md`._

**Ordering key:** 🟢 = mods on disk is enough (no running game). 🔵 = needs a running game.
🟣 = needs RimBridge live. Do 🟢 first — several don't even need the game launched.

---

## 1. 🟢 Resolve the shortHash blocker (unblocks the save parsers)
Saves store defs as **shortHashes**, not names. Rebuild the `shortHash → defName` map offline by
scanning every active mod's `Defs/` the way the game does (deterministic from defName+defType).
Turns `Savegame_*.py` from opaque codes into a legible world model. **First thing to run** once
mods are downloaded — before launching. → owns the fix noted in `RimMaster.md` / memory.

## 2. 🟢 Build the Def index / world ontology
Index every Def in the real load order (things, terrains, factions, xenotypes, pawnkinds,
interactions, traits). This is what the agent reasons over. Doubles as validation: confirms
`OuterRim_Jawa`, JawaVoice gates, and the `faction_roster_v2` cast **actually resolve** — catches
typos before they become silent in-game no-ops. Cross-check against `concept_defnames.md`.

## 3. 🔵 Boot & red-error pass
Launch once to menu with full list (RimSort-ordered). Resolve red errors (esp. Outland Genetics —
Jawa def hard-refs its genes). Confirm JawaVoice + GravshipCompat load last. = `setup_checklist` §0.

## 4. 🔵 Validate the content we authored blind
- **JawaVoice:** trigger real SpeakUp bubbles; confirm Jawa pawns speak Jawaese + non-Jawa fall
  through to English. Spot-check the synthesized voice against the review sheet.
- **Faction diffs / roster:** confirm the authored FactionDefs cast correctly (gated on Sensible
  Factions).
- **Scenario/starting save:** load it; confirm desert world, Jawa xenotype + ideoligion, VGE sole
  ship layer all present.

## 5. 🔵 Harmonize a real save as the tooling target
Take one embarked save = the canonical fixture. Run `Savegame_*.py` end-to-end against it (now
legible via #1). This is the "harmonized savegame" the agent and utils develop against.

## 6. 🟣 Bring up RimBridge & swap the mock for the real transport
Install RimBridgeServer. Point RimMaster's loop (built offline against the GABP mock + capability
contract) at the live bridge. Fix only the deltas between mock and real protocol — isolated behind
the thin adapter. Verify read path first, then guarded writes (save-backup-first).

---

## Pre-req checklist (build these BEFORE the week starts — no game needed)
- [ ] RimMaster **capability contract** (transport-independent read/write schema) — parent of the mock + resolver.
- [ ] **GABP mock** endpoint + synthetic save fixtures — develop/test the agent loop offline.
- [ ] **JawaVoice review sheet** + vanilla combat/mining reskin (`Utinni!`/`Ny shootogawa!`).
- [ ] Advance **scenario spec** + **faction diffs** (offline-authorable now).

**Open decisions that change the above:** RimMaster's primary transport (save-edit vs live
RimBridge vs both) — sets what the mock imitates first; whether the mod list is downloadable this
week — decides if #1/#2 start now or wait.

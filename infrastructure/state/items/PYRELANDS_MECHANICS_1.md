# PYRELANDS_MECHANICS_1 — the igniter C# kit, as ruled

## spec
The authoritative brief is `design/Jawa/worldbuilding/creatures/RUT_ruled_commissions_wave2.md`
§§7–8 (owner-ruled 2026-09-10, commit 4a6f6200) plus `design/Jawa/worldbuilding/biomes/the_pyrelands.md`.
Both defs EXIST with art (`RUT_PyrelandsFauna.xml`); this item is the owed mechanics
and the five ruled def changes.

**Fire-hawk (`RUT_FireHawk`) — spread comp (§7c):**
- Small C# comp/JobGiver cribbing the pattern of `JobGiver_FireStartingSpree` (an
  internal mental-state class — crib, never reuse). If a fire exists within scan
  radius: short sortie, ignite one flammable cell N cells beyond the fire's edge,
  long cooldown. Direction random in v1 (downwind only if wind is cheap to read —
  INVENTED parameters, spike decides).
- 🔴 **Spread-only, never ex nihilo — RATIFIED (owner, 2026-09-10).** The hawk needs
  a flame to steal from; lightning and the furnace-beast start fires, the hawk
  SPREADS. This is the def's law.
- Flush-prey benefit ships as story + ordinary predation in v1 (no targeting code).

**Furnace-beast (`RUT_FurnaceBeast`) — thermal circuit (§8b–8c):**
- Ship vanilla `CompHeatPusher` (one XML node) — delivers real heating in enclosed
  spaces. Open-field "walking hearth" is the owed C#: aura comp applying a warmth
  hediff (comfy-temperature offset) to pawns within a few cells (INVENTED radius).
  Hediff aura, NOT cell temperature — fighting the outdoor model was rejected.
- Bed-down ignition: on completing a rest cycle (verify the tick hook at build —
  never guess), chance to ignite/scorch its bed cells (1–2 cells, smolder not blaze
  — INVENTED numbers). FireEcology scorched register already built
  (`src/RimMandrake/Pyrelands/`, RM_FE_ tier). 🔴 NO tamed-exemption — the hazard
  is the point (owner, verbatim: "Fires all the time! I love it.").

**Five ruled def changes on the furnace-beast (§8a, ban-5 reversal):**
1. REMOVE VEF `CompProperties_Untameable` — tameable by ruling.
2. Raise `trainability` off None (Intermediate matches the hawk — proposal).
3. Rewrite description's closing line ("Nothing on this planet has ever kept one" is
   now wrong) toward "keeping one is possible, hard, and a standing fire hazard".
4. Keep `manhunterOnTameFailChance 0.9` — it is the taming gauntlet.
5. Swap `Leather_Heavy` → `RUT_FurnaceHide` (§12 of the brief).
Wildness: high but strictly < 1.0 — `TameUtility.CanTame` hard-refuses ≥ 1.0
(verified at source, TameUtility.cs:49).

The original 09-07 filing also names: migrating burn-line presence, burn
intelligence, flame-harvest + fire-raid events, ruled weather table (spec
`the_pyrelands.md`) — larger kit, same item; the two creature comps above are the
ruled, unblocked first slice.

## verify
- [ ] Hawk never ignites without a pre-existing fire in scan range (spread-only law).
- [ ] Furnace-beast heats an enclosed room (CompHeatPusher) and applies the warmth
      hediff in the open; bed-down ignition fires for TAMED beasts too.
- [ ] `--defs`+`--live` validation green; wildness < 1.0 confirmed in the built def.

## criteria
- [ ] The five §8a def changes land in the same wave as the comps, or the roster
      rows' recorded debt line is updated to say what remains.

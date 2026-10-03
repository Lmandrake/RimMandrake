# Empire escalation ladder — design (EMPIRE_ESCALATION_LADDER_1)

Status: DESIGN ONLY, for the owner to rule on. BENCH helper, 2026-10-02. No defs, code,
items or ledger verbs came out of this pass.

The brief, in his words (2026-09-27, Chill secrecy sitting): *"Escallation isn't just 'more
troopers' it's more kinds of raids that rapidly escalate until you move. Always start with
probes that can be evaded."*

**The finding that shapes everything below:** most of the parts are already built. They are
just not connected to each other. Today the Empire's pursuit runs as a flat metronome. Every
tile gets the same drop-pod assault on a timer, and then **endless waves every 3 hours at 2×
points with a 10,000-point floor**. That is the "more troopers" kill wall he rejected. So the
ladder does not need a new system. It replaces the pursuit mod's single `FireRaid` with a
sequence of rungs, and it is the first thing to feed it from the Colony Visibility dial,
which already exists.

---

## 1. What exists (measured, with paths)

| piece | where | state | what the ladder takes from it |
|---|---|---|---|
| **Empire faction** | vanilla Royalty `Empire`, reskinned. Patches: `src/RimUtinni/UtinniPatches/Patches/GalacticEmpire.xml`, `src/RimStarWars/StarWarsPatches/Patches/VanillaFaction_Xenotypes.xml`, `src/RimUtinni/PawnFlavor/Patches/FactionBackstoryWiring.xml` | live. `OuterRim_GalacticEmpire` FactionDef is cut, but its MOD stays as the gear donor (memory note *Galactic Empire is reskinned vanilla*; `design/Jawa/reconciled_lore/04_factions.md` §1) | the faction every rung fires as |
| **Pursuit timer** | `src/RimUtinni/EmpirePursuit/` (`mandrake.rut.empirepursuit`, fork of Ruthless Faction Pursuit) | active in `infrastructure/state/modlists/ModsConfig.FULL.LATEST.xml` (610 mods, 2026-10-02). ScenPart installed (`EMPIRE_PURSUIT_SCENPART_INSTALL_1` done) | **the ladder's host.** Per-map warning + raid timers, 5–8 d cadence (owner 2026-08-28), and `surveyShadowBiomes` ×4 for the Abyss (`EMPIRE_PURSUIT_SURVEY_SHADOW_1` done). `FireRaid_NewTemp` (`RuthlessPursuingMechanoids.cs:732`) always fires the same thing: `RaidEnemy`, `ImmediateAttack`, `RandomDrop`, ≥5,000 pts ×1.5, followed by endless ×2.0 / floor 10,000 every `EndlessWavesHours` = 3 |
| **Colony Visibility dial** | `src/RimMandrake/Visibility/` (`mandrake.rm.visibility`). Design: `design/Jawa/worldbuilding/colony_visibility_stat.md` | active. 0–100 GameComponent with five bands (Hidden / Discreet / Noticed / Marked / Exposed). The launch reset is wired (postfix on `GravshipUtility.GenerateGravship`), and so is per-tile memory that halves each season away. **It only touches detection raids** (`TimedDetectionRaids`). Per the closed `COLONY_VISIBILITY_STAT_1`, 14 of its raise/lower hooks are called from nowhere | **the attention input.** It already has a launch reset, tile memory, an `Adjust()` API and a `ShkaarEscalationMultiplier` seam |
| **Battle recorder** | `src/RimMandrake/Aftermath/` (`mandrake.rm.aftermath`) | active. Classifies every raid as REPELLED / ROUTED / STALEMATE / LOST and queues follow-ups through `incidentQueue` with `forced = true` | **the outcome signal** for climbing a rung |
| **Old Friends roster** | `src/RimMandrake/RaidRedesigner/` (`mandrake.rm.raidredesigner`) | built, **not in the FULL list**. The Oracle letter layer is HELD (`PLOT_MECHANISM_MODS_WAVE_1`) | optional: lets a recurring Imperial officer command the higher rungs |
| **Raid cooldown** | `mlie.factionraidcooldown` | active | ⚠️ may suppress repeat Empire raids. Whether it hooks `Worker.TryExecute` (pursuit's path) or only the storyteller's pick is **UNMEASURED** |
| **Probe droid defs** | `src/RimStarWars/Droidworks/Defs/PawnKinds_KotOR.xml`: `RSW_DW_KotORDroidBad_KX12UPD` "probe droid", `_KX12APD` "assassin probe", `_KX12APD_sapper` "saboteur probe"; canon entry `design/RimStarWars/canon_references/droid_kx12_probe` | exist as hostile droid kinds | rung 1 can use them now. The canon Imperial probe, the **11-3K viper**, is in `DROIDS_INDEX.md` as canon and has **no def** |
| **Imperial strike loadout** | "ruling-2 loadout: stormtroopers + attack droids" (`droid_mass_production_quest_chain_2026-10-02.md` §2.5) | authored `Empire_*` kinds field under `Empire` | rungs 3–5 |
| **Empire heat (proposed)** | `design/Jawa/proposals/droid_mass_production_quest_chain_2026-10-02.md` §4.4 brake 2, a "line-heat counter" that weights an Imperial Foundry-strike incident | proposal only | **must be the same meter as this one**, not a second one (§2) |
| **Route 6 leak** | `design/Jawa/worldbuilding/biomes/the_chill_warlab_routes_spec_2026-09-27.md` §Route 6 | ruled 2026-09-27: leaks are discrete named events, preventable but never undone, and leave the Empire "maximally escalated" | a permanent rung floor (§4) |
| **Lore** | `design/Jawa/reconciled_lore/01_campaign.md` "three pressures": the Empire is *"the singular escalating military pursuer, orbital-first"*; it forces exit from open sky *"in under one growing season"*; dark/covered tiles PAUSE the orbital clock (owner 2026-08-05/06) | ruled | sets the ladder's total length and the dark-tile pause |

**Engine facts used (RimSage, decompiled 1.6):**
- Vanilla arrival modes: `EdgeWalkIn`, `EdgeDrop`, `EdgeWalkInGroups`, `EdgeDropGroups`, `CenterDrop`, `RandomDrop`, `MechClusterDrop`, `EmergeFromWater`, `EdgeWalkInDistributed`. A worker class `PawnsArrivalModeWorker_EdgeWalkInDarkness` exists and spawns in `PsychGlow.Dark` cells.
- Raid strategies: `ImmediateAttack`, `ImmediateAttackSmart`, `StageThenAttack`, `ImmediateAttackSappers`, `ImmediateAttackBreaching(Smart)`, `Siege`, plus Anomaly's. Sappers and Breaching derive from `RaidStrategyWorker_WithRequiredPawnKinds`, so the faction must field the required kinds.
- `IncidentParms` carries `raidStrategy`, `raidArrivalMode` and `pawnGroupKind`. **A rung is therefore expressible as parms on the existing `RaidEnemy` worker.** Only the probe rung needs new behaviour.
- **Moving already resets the pursuit clock.** `GravshipUtility.ArriveNewMap` → `GetOrGenerateMap` → `MapGenerator` → `Scenario.PostMapGenerate` (`MapGenerator.cs:188`) → pursuit's `PostMapGenerate` → `StartTimers(map)`. A landing at an existing map (`ArriveExistingMap`) generates nothing, so its old timers carry on.
- Royalty's `Bombardment` (`Ethereal_OrbitalStrikes.xml`) is a vanilla ThingDef. Odyssey ships `Drone_Hunter` / `Drone_Wasp` / `Drone_Sentry` kinds.
- **UNMEASURED:** whether any vanilla `LordJob` already does "wander, look, then leave". I found none in this pass, so the probe's lord is costed as new C#.

---

## 2. The attention model

**One meter, which is already built: Colony Visibility.** No "Imperial heat" variable is added. The droid
chain's line-heat counter becomes calls to `Visibility.Adjust()` tagged as Imperial. A second
meter would split what the player has to watch.

The ladder adds **one per-map integer, the rung** (0–6), stored on the pursuit ScenPart next to
the map's timers. So there are two numbers, and each answers a different question:

| | Visibility (0–100, ship-wide) | Rung (0–6, per map) |
|---|---|---|
| answers | *how loud are we?* | *how far has the Empire got with finding us HERE?* |
| moves by | deeds and curses (table below) | rung outcomes (§3) |
| sets | **how fast** the next rung comes (the timer) and the points | **what kind** of thing comes next |

**What raises Visibility.** These are the existing §2 hooks of `colony_visibility_stat.md`,
with wiring that is still owed. Ladder-specific additions:
- a probe that **leaves the map with a sighting**: +M, and the rung climbs
- a spotter who gets his signal out (rung 2): +M
- each droid-line batch run (droid chain §4.4): +S, flagged Imperial
- a named leak event (Route 6 Paths A/B): +L, plus a permanent rung floor
- *ruled lore, not new:* open sky. The orbital clock runs only on uncovered tiles.

**What lowers it.** Existing hooks: darkness, concealment, ambush kills, Blackout reign,
Ishko's boons, and a raid survived undetected. Ladder-specific:
- a probe **destroyed before it transmits**: −S, and the rung does not climb
- a probe that **leaves with no sighting**: no change, but the next probe comes later
- **launching**: the existing `ResetOnLaunch()`, to 5–15

**Timer coupling (the only new arithmetic).** The pursuit's 5–8 d interval is multiplied by
band: Hidden ×2.0 · Discreet ×1.4 · Noticed ×1.0 · Marked ×0.7 · Exposed ×0.5. The
survey-shadow ×4 stacks on top. A Hidden clan on an Abyss tile therefore gets roughly 40–64 days
between rungs. An Exposed clan on open sand gets 2.5–4. **The Visibility × points curve
(0.55→1.60, already ruled) applies to every ladder rung**, which closes the gap where pursuit
raids ignored the dial.

**How the player reads it (no new UI surface, following F17):**
1. **An Alert** while a map is past rung 0: *"Imperial search: rung 2 of 6 — Marked. Next contact
   in ~3 days."* Pursuit already yields an `AlertCached`. Extend its text.
2. **Every rung arrives with its own named letter**, never a generic "raid". The letter says
   what came, what it wants, and what beats it.
3. **The Visibility band clause** on the reign-calendar line (F17, already proposed).
4. On the world map, the tile inspect string carries the remembered rung: *"Imperial search
   here: rung 3 (fading)."* This tells the player where not to land again.

---

## 3. The rungs

Each rung is a **different kind** of contact, as the brief requires. The first two can be
evaded without a stand-up fight. Rung N+1 fires on the next timer only if rung N **succeeded**
from the Empire's side. Otherwise the rung repeats or holds. "Rapidly" comes from the timer
shortening as Visibility rises, and from rungs 3+ using half the base interval.

| # | name | what arrives (engine shape) | the Empire succeeds if… | how to evade or beat it | warning the player gets |
|---|---|---|---|---|---|
| 0 | **Quiet** | nothing. The timer runs; it pauses under roof/dark per lore | — | stay dark, stay small | Alert: *"The sky is empty. For now."* (shown from Discreet up) |
| 1 | **Probe** | 1–2 probe droids. `RandomDrop` far from the colony (≥40 cells), **new `LordJob_ImperialProbe`**: wander toward the colony's edge, then hover-scan. A *sighting* is LOS to the gravship or a colonist for ~2 in-game hours in total. After 1 day it leaves via `ExitMapBest`. Pawn: KX12 `RSW_DW_KotORDroidBad_KX12UPD` now, the 11-3K viper once it has a def | it leaves the map alive **with** a sighting | **shoot it before the sighting completes** (it self-destructs, small blast. Canon, and it means a kill is never free loot) · **stay out of sight** (indoors, dark, under the hull) · **let it leave blind**. All three evade. Only the first is a fight, and it is a fight with one droid | Letter *"Probe landed"*, sent on landing, with a look-target on the pod and a countdown bar showing sighting progress |
| 2 | **Spotter** | a small scout-trooper team, `EdgeWalkIn` + `StageThenAttack`. One carries a **comm-link (a "spotter" tag)**. They stage at range and do not assault. The spotter "calls it in" after ~6 h staged | the spotter's call completes | **kill or down the spotter** before the call (the team then routes) · or **launch now** (cheapest, and exactly "until you move") · or stay hidden: if the staging cell has no LOS to the ship, the call fails | Letter *"Scouts staging at the ridge"*. Alert with the call countdown |
| 3 | **Strike** | the first real raid: stormtroopers + attack droids ("ruling-2 loadout"), `EdgeDropGroups` + `ImmediateAttackSmart`, points = storyteller × Visibility curve | not REPELLED (per the Aftermath classifier) | beat it in a fight, or leave before it lands (a 12 h warning) | Letter on the probe's/spotter's success, *"Strike team inbound — 12 h"* |
| 4 | **Cordon** | **the ship is the target.** Imperial **ion emplacement** siege (lore: ion emplacements are Imperial anti-ship tech): `Siege` strategy with an ion mortar, aimed at the gravship's footprint. Ion = EMP, so it disables the grav engine **temporarily**, never destroys it | the emplacement stands for 2 days | assault the siege camp, **or launch before the first ion volley** (warning gap ~1 day). ⛔ Never trap: the ion lockout lasts hours, never days, so the escape stays open | Letter *"They are building a cordon"*. The emplacement is visible on landing |
| 5 | **Breach** | heavy assault: `ImmediateAttackBreaching` with breacher kinds, plus a second group by `CenterDrop`. **Two raid kinds at once** | not REPELLED | win a hard fight, or leave | Letter, 6 h warning |
| 6 | **Bombardment** | **orbital strike.** Vanilla `Bombardment` targeted on the gravship's area, then the existing endless waves as the terminal state. This is the only rung where "more troopers" is allowed, because by now it is punishment for staying | — (terminal) | **leave.** A 1-day telegraph with a target circle drawn on the map | Letter *"Star Destroyer in orbit"*, 1 day out, and the target area is marked |

**Why this shape honours "until you move":** from rung 2 up, launching beats every rung outright.
Rungs 1–2 can be beaten while staying, at low cost, which is what "can be evaded" means. Rungs
3–5 can be beaten while staying, but only by winning, and each win buys just one more rung's
interval. Rung 6 cannot be won.

**What the ladder retires:** pursuit's second wave and its every-3-hours endless waves *before*
rung 6. Those are exactly the "more troopers" he rejected.

---

## 4. How moving resets it

- **A launch to a new tile** puts the new map at rung 0. This is already true mechanically
  (`PostMapGenerate` → `StartTimers`). The ladder just keeps it. Visibility drops through the
  existing `ResetOnLaunch()`.
- **The old tile remembers.** The departure rung is written into the existing
  `tileMemory` (Visibility, keyed by `PlanetTile`) and decays one rung per season away. Landing
  back on a remembered tile starts at the remembered rung. This is the ruled *"the desert
  remembers, decaying"*, applied to the rung.
- **A permanent floor from leaks.** A Route 6 leak (Path A or B) or the droid line being
  discovered (chain beat 5) sets `rungFloor` = 2 everywhere for the rest of the game. Probes
  stop being the opening, because the Empire knows what it is looking for. Route 6's
  "maximally escalated" = floor 3. *This is the "prevent, never undo" ruling expressed as a
  number.*
- **Survey shadow** (the Abyss) keeps its ×4, so a refuge is a slower ladder, never a frozen one.
- **Returning to an existing map** (`ArriveExistingMap`) does not regenerate the map, so its rung and
  timers persist. This is correct: you came back to where they were looking.

---

## 5. With the storyteller and the gods

- **The storyteller keeps its own Empire raids** (owner ruled `canDoNormalRaid` **true**,
  2026-08-28). Rule: a storyteller-picked Empire raid **never climbs the ladder**. It is
  "the occupier being the occupier", not the search. The ladder never fires inside 2 days of a
  storyteller Empire raid on the same map, and the reverse holds too. This stops stacked spikes.
- **`mlie.factionraidcooldown`:** the ladder's raids must bypass it. Aftermath already needed
  the same bypass for its forced follow-ups, so reuse that bypass. Exact hook: **UNMEASURED**,
  verify at build.
- **Aftermath** classifies rungs 3 and 5, and those outcomes drive the climb. A REPELLED strike also fires
  Sh'kaar's per-battle delta as it does today.
- **Ta'Baa:** launching is his holiest deed, and it is also the ladder's reset. The theology and
  the mechanic say the same thing, so nothing new is needed.
- **Ishko** (concealment) lowers Visibility, which slows the timer. **Unseen Berth** (his large
  boon, "one detection-clock reset") = **drop this map's rung by one**. That gives the boon a
  concrete payoff.
- **Sh'kaar's escalation multiplier** multiplies ladder *points* (the existing seam), never the
  rung. Sh'kaar makes the strike bigger; he does not make the Empire find you faster.
- **Ozzik's Renown / THE SHAMING** raise Visibility, which shortens the timer.
- **Hutt ledger** is unaffected. The three pressures stay distinct, as the lore rules.

---

## 6. Mod Settings

On `mandrake.rut.empirepursuit`'s settings screen (a `Settings.cs` already exists):

| setting | default | note |
|---|---|---|
| Escalation ladder (vs. classic flat pursuit) | **on** | off = today's behaviour |
| Probes open every ladder | on | off = start at rung 3 |
| Ladder pace multiplier | 1.0 (0.25–4) | scales every rung interval |
| Visibility drives pace | on | off = flat 5–8 d |
| Rungs remembered per tile | on | "the desert remembers" |
| Rung decay per season away | 1 | 0–3 |
| Cordon (ion siege) rung | on | |
| Orbital bombardment rung | on | **affects the map** (destroys buildings), labelled as such |
| Endless waves after the top rung | on | |
| Show search Alert | on | |

All off = vanilla-shaped pursuit, which degrades gracefully as the standing rule requires.

---

## 7. Build plan (FOUNDRY)

Every phase ships with its slice of the mod's **functional script** (`validation.py` already
exists in the mod folder), per the 2026-10-01 debugging process.

| P | what | size | depends |
|---|---|---|---|
| **P1** | `RUT_EmpireRungDef` (index, label, letter keys, arrival mode, strategy, `pawnGroupKind` / required kinds, points factor, interval factor, success condition enum). Replace `FireRaid_NewTemp` with a `RungRunner`. Add per-map `rung` + global `rungFloor` to the ScenPart's `ExposeData`. Save-compatible: a missing value means rung 0 | M | — |
| **P2** | Probe rung: `LordJob_ImperialProbe` (wander → scan → exit), sighting accumulator (LOS to colonist/gravship), self-destruct on death, letter + progress. KX12 kind first | M–L | P1 |
| **P3** | Spotter rung: tag one pawn and give it a call toil with a countdown; a downed/dead spotter → the lord routes | M | P1 |
| **P4** | Visibility coupling: band → interval multiplier, curve → points, probe/spotter `Adjust()` calls, Unseen Berth rung drop, tile memory gains a rung field | S–M | P1, `mandrake.rm.visibility` |
| **P5** | Cordon + Bombardment rungs. Ion emplacement def (an Imperial reskin of a vanilla mortar firing EMP shells, **check for existing ion art/defs first**) and its siege targeting of the gravship. Bombardment telegraph | M | P1 |
| **P6** | Aftermath hook (REPELLED → hold), storyteller spacing (2 d), raid-cooldown bypass | S | P1, `mandrake.rm.aftermath` |
| **P7** | Leak floors: a public `EmpireSearch.RaiseFloor(int, string reason)` for Route 6 and the droid chain to call | S | P1 |
| **P8** | Settings + the Alert/inspect strings | S | all |

The suggested order P1 → P2 → P4 → P3 → P6 → P5 → P7 → P8 gives a playable "probe, then the
classic raid" after P1+P2. **Open check before P1:** `EMPIRE_PURSUIT_SCENPART_INSTALL_1`
installed the ScenPart into a save that predates the world remake, so the shipped save will be
re-cut at the remake (memory: *world remake is the last step*). New scribed fields need defaults.

---

## 8. Questions for the owner

**Q1. When the clan lands on a new tile, how much does the Empire still know?**
- **A (recommended). Full reset to rung 0, with probes again, but a leak sets a permanent floor.**
  Moving is always worth it, which is the point of "until you move". The trade-off: a late
  game can grow easy if the player hops often.
- B. Drop two rungs, never below 0. Moving still helps, but a careless clan stays hunted. The
  trade-off: a short hop can land straight into a strike team, which may feel unfair.
- C. Rung 0, but the timer starts shorter the higher you were. This is a middle path. The trade-off:
  it is harder to read.

**Q2. Can a ladder rung touch the ship itself?**
- **A (recommended). Yes, but only to stall it.** The ion cordon disables the engine for hours, so
  staying gets frightening but escape is never closed. The trade-off: it needs an ion emplacement
  def and art.
- B. No. The ship is never a target, and the ladder only throws raids and the bombardment. This is
  simpler, but rung 4 loses its "they are pinning you down" kind.
- C. Yes, and for real: the cordon can damage hull and engine. This has the most tension. The
  trade-off: it can strand a clan, which works against "until you move".

**Q3. Does the orbital bombardment rung destroy buildings on the map?**
- **A (recommended). Yes, on a full day's warning and a marked target area.** It is the
  unmistakable "leave now". The trade-off: it can wipe out a base that took real effort.
- B. It hits only open ground and pawns, never structures. This is gentler. The trade-off: it becomes
  something to wait out rather than flee.
- C. No bombardment, and the top rung is the existing endless waves. The trade-off: this is the
  "more troopers" ending he said escalation should not be.

**Q4. The droid line's "Empire heat" and Visibility: one meter or two?**
- **A (recommended). One.** Running the line raises Visibility, and its discovery sets a ladder
  floor. The player watches one number. The trade-off: the droid chain's strike becomes a ladder
  rung, not its own incident.
- B. Two. The line keeps its own heat counter and a site-specific Foundry strike, separate from the
  ship's ladder. This gives richer site play. The trade-off: two clocks to read, and a home-map strike
  could stack with a ladder rung.

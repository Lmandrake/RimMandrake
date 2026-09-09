# STAGED_LORE_DESCRIPTIONS_1 — descriptions that change as the story is learned

Filed by BENCH from the Scarlands sitting, 2026-09-06. **Provenance, not
authorization** — the owner mused: *"I wonder if the scenario could actually
change its own terrain descriptions as Lore is revealed, wouldn't that be
amazing, depending on where they were in the story?"* This item answers the
wonder; whether to BUILD it is his ruling once feasibility is known.

## The question

Can biome/terrain/thing descriptions (and settle warnings, item flavor) swap by
campaign lore-stage — so the Scarlands reads as "inexplicable wasteland" until
the player learns the truth, then as what it is?

## Feasibility sketch to verify (not assume)

- Descriptions are def fields read at display time in most inspector paths —
  a Harmony postfix on the description getter keyed to a WorldComponent
  lore-stage is the likely cheap route; verify which UI paths cache strings.
- The reveal gates already exist as design: `the_scarlands.md` §GM ladder
  (neutral droids → Cathedral → educated factions → bastion record).
- Consumers beyond the Scarlands if it works: the Contagion, the Propane Lakes'
  war lab, the Webwork's not-native mystery — every §GM-partitioned biome.

Deliverable: a one-page feasibility verdict with the patch surface named, then
his go/no-go.

## Feasibility verdict (BENCH, 2026-09-08 — VERIFIED against 1.6 source via rimsage)

**FEASIBLE, and cheaper than the Harmony sketch.** The display paths read the def
FIELD live, so the cheap route is not a patch at all — mutate the def:

- `Thing.DescriptionFlavor => def.description` (Thing.cs:586, virtual, read at
  display time) — items/buildings pick up a changed field immediately.
- The info card reads `def.description` / `DescriptionFlavor` at draw
  (StatsReportUtility.cs:314/329) — live.
- 🔑 **Biomes**: the world tile inspector reads `selTile.PrimaryBiome.description`
  directly at draw (WITab_Terrain.cs:62, WITab_Orbit.cs:55) — a changed BiomeDef
  field shows on the very next frame. Settle-time text rides the same def.
- Vanilla precedent: `Pawn.DescriptionFlavor` already swaps description by mutant
  state (Pawn.cs:2292) — staged descriptions are an engine-native idea.

**The one cache trap (verified):** `ThingDef.DescriptionDetailed` memoizes into
private `descriptionDetailedCached` (ThingDef.cs:794–821), used by trade/transfer
/filter tooltips. A stage swap must null that field via reflection on affected
ThingDefs, or those tooltips keep the old text for the session.

## Status 2026-09-09 (Fable) — feasibility half EXECUTED, full trace filed

`design/Jawa/worldbuilding/research/staged_lore_descriptions_feasibility_2026-09-09.md`
— every display path traced to `File.cs:line` in the 1.6 source. **FEASIBLE on
all five named surfaces**; biome inspect, settle warning, thing flavor and info
card are live-read, trade/transfer is the one cached path. **Two** long-lived
caches found, not one: `ThingDef.descriptionDetailedCached` (`ThingDef.cs:414`)
**and** `HediffDef.descriptionCached` (`HediffDef.cs:193`) — neither is cleared
by any engine path, because `ThingDef` and `HediffDef` do not override
`Def.ClearCachedData` (only `RoadDef`/`BodyDef` do). Reflection is the only
invalidation route. Vanilla precedent is stronger than the 09-08 note recorded:
`Building_VoidMonolith.cs:92–102` stages its description by Anomaly *campaign
level* — this exact feature ships in the base game. New trap: defs are not
reloaded between savegames (`LoadAllPlayData` is called only from `Root.cs:75`
and on language change), so the apply must reset to baseline every load or a
stage-4 colony leaks its text into a stage-0 one. Effort ~1.5 days + one
authoring sitting. R25 compliance is a property of the data table, not the
mechanism — the top stage still never names the Assailants. Awaiting go/no-go.

**Recommended shape:** a `GameComponent` holding the lore stage (scribed), a
data-side table `defName → {stage: description}` (rules as data), applied on
load + on stage-advance by rewriting `def.description` and clearing the one
cache. No Harmony unless we later want per-viewer variation. Consumers: the
Scarlands GM ladder first, then Contagion / war lab / Webwork as their gates
land. Awaiting the owner's go/no-go.

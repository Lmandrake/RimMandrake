# TITANIC_CREATURES_MOD_1 — make titan mass REAL

Owner, 2026-09-09: our giants are TRULY giant — beyond what RimWorld allows or
encourages (bs 12 Krayt, bs 15 GreaterKrayt/WarWyrm/SummitCrab, bs 16
Paraceramuffalo, bs 20 ElderSando, bs 32 Reefback, bs 40 Lanternwhale). The engine
gives every pawn ONE cell: a titan walks through a doorway, hides behind a sandbag,
gets penned like a chicken. This mod makes mass have consequences.

## Ruled by card (owner, 2026-09-09) — these are decisions, not options

1. **Both mechanisms from day one.** True multi-cell footprints AND the destruction
   wake. **Thin (constructed) roofs are DESTROYED as the titan passes; thick roofs
   (overhead mountain) are AVOIDED** — a titan never paths under rock, and smashes
   through anything built.
2. **Tiers auto-attach by bodySize, with a curated developer override (yes/no per
   def).** A dense small thing can opt in; a light big thing can opt out.
3. **Crushables are CURATED, not assumed.** A data table says which thing
   categories/defs crush under a titan and which don't — walls yes, but e.g. chunks,
   ancient ruins pieces, specific quest items ruled individually. Never "everything
   in radius".
4. **T3 corpse-as-site.** The largest tier's corpse becomes a map landmark harvested
   over days — camps, spoilage, scavenger draw — never an instant meat mountain.
   T1–T2 get curved (sub-linear) yields.
5. **Titan biomes + events.** Titans roam only where the rosters home them; anywhere
   else they arrive as scripted events/quests with warning (footfall tremors first).
   Wake damage applies to any structure including the player's — that is the point.

## The multi-cell foundation: Large Pawns — RIDE-WITH-CONFIG (decompile verdict, 2026-09-09)

`neku.largepawns`, workshop `3777700657`, **ACTIVE**. Full decompile findings:
`design/Jawa/worldbuilding/research/large_pawns_decompile_2026-09-09.md` (`017af47c`).
The verdict and its consequences, binding on the build:

- **Ride it, configured** — it already implements card #2 exactly (bodySize tiers +
  per-def override table in both directions: 1 = force 1x1, 2–4 = force size). The
  alternative is reimplementing 68 Harmony patches; and it ships **no license**, so
  "absorb" could only ever mean independent reimplementation, never copying.
- 🔑 **Integration surface: `GenAdj.OccupiedRect(Thing)`** — Large Pawns
  Prefix-patches vanilla's own method to return the true square, so our wake comp
  reads the footprint with NO reference to LargePawns and degrades cleanly to 1x1
  if the mod is absent. Build against vanilla's API only.
- **One size ladder**: reflectively set `LargePawns.Main.settings` thresholds and
  push our per-def override rows, then `NotifyEdited()` — its config table becomes a
  projection of OUR tier table at startup. ⛔ Never two ladders.
- ⚠️ **4x4 is its hard ceiling** (no size-5 branch): bs 20/32/40 all land 4x4. T3's
  extra presence must come from OUR wake radius/footfall, not footprint.
- ⚠️ **It has its own wall-break feature** (`PathClearingUtility`, three settings
  bools) — turn it OFF and let our curated crush-table be the only destruction
  authority (theirs is uncurated, which card #3 forbids).
- ⚠️ **Doors: blocked, never squeezed** — a 1-tile gap stops a 2x2; it mass-opens
  doors under the footprint. Its region/door connectivity is the author's least
  settled area (his own test scripts chase a 2-wide-door bug). Quicktest exactly this.
- ⚠️ **Predicted defects it does nothing about**: pens (a titan can be penned behind
  a fence gate its square can't pass), caravan forming, and a per-tick O(all pawns)
  cache scan (`UpdateLargePawnsCache`) — measure TPS on the full list before and
  after activating our tiers; nothing is scribed so uninstall is clean.
- Live behavior still UNPROVEN on our 590-mod list: first build step remains the
  bridge quicktest (spawn bs 12, prove occupancy by getter, path a 1-tile gap).
- Vehicle Framework is force-excluded by it (vehicles pinned to size 1) — no
  interaction to design for.

## Tier table (draft — the mod's single size authority; per-def override list beside it)

| tier | bodySize | footprint | wake |
|---|---|---|---|
| T1 heavy | 4–8 | 2x2 | crushes curated flora/items, filth trail, footfall |
| T2 colossal | 8–20 | 3x3 | + curated furniture/walls damaged, thin roofs holed |
| T3 titanic | 20+ | 4x4+ | + curated structures destroyed outright, corpse-site |

(Boundaries are BENCH draft, not ruled — tune at build against the actual roster
census; the assignment pass's size-ladder figure is the instrument.)

## Mechanics (design pass, BENCH 2026-09-09)

- **Destruction wake**: comp on tier-qualified races; each cell entered, curated
  crushables within girth radius take crush damage/destruction. Roof supports
  crushed → thin-roof collapse emergent; explicit thin-roof removal where the
  footprint passes. Event-driven per cell entered — no per-tick scans (perf rail).
- **Thick-roof aversion**: pathing cost/exclusion on overhead-mountain cells for
  tiered races. With the wake, the only way a titan is ever inside a base is that
  the base is no longer there.
- **Footfall presence**: screen shake, thud audio, dust puffs, flee trigger for
  nearby animals, pawn stagger chance. Sells the mass before line of sight.
- **Kill-box eater**: melee reach 2–3 cells at T2+; smashes cover being used
  against it (curated — cover is in the crush table).
- **Spacing law**: hard cap one T3 per map; T2 count capped low. Matches the
  rosters' single-spawn near-zero commonalities; the mod enforces what the sheets
  legislate.
- **Yield normalization**: sub-linear meat/leather curve for T1–T2 (the fig4
  linear-yield defect at scale); T3 yields only through the corpse-site.
- **Corpse-site (T3)**: corpse becomes a harvestable landmark (days of work,
  spoilage clock, scavenger waves, quest hook potential). Design kinship: the
  gravship wreck fields — a titan corpse is terrain with a story.
- v2 candidates (parked, not scoped): faction blame when a titan smashes an NPC
  base; titan migration events between home biomes; mounted/ridden titans (no).

## Naming
RM tier (generic RimWorld capability): mod folder `RM_TitanicCreatures`, packageId
`mandrake.rm.titaniccreatures`, defs/comps prefixed `RM_`. Campaign flavor (which
creatures, which biomes) stays in the rosters, not in this mod.

## verify
- Quicktest: bs 12 spawn occupies >1 cell (getter-proven), cannot path a 1-tile
  gap, thin roof destroyed on transit, thick roof never entered, curated
  non-crushable survives adjacent transit, crushable does not.
- One T3 kill → corpse-site spawns, instant butcher yields nothing beyond the site.
- Tier auto-attach: census of tiered races matches the tier table against the
  roster size ladder; override list honored both directions.
- No second size ladder live (Large Pawns thresholds reconciled or absorbed).

## Tier census (fig10, MEASURED 2026-09-09, rostered defs)
T1 4–8: **18** · T2 8–20: **7** · T3 20+: **3** (RSW_ElderSando, RSW_Reefback,
RSW_Lanternwhale). Large Pawns at its default thresholds would make **57** defs
multi-cell (16 at 3x3, 9 at 4x4) — the measured size of the one-ladder reconciliation.

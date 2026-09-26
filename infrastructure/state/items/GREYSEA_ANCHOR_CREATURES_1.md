# GREYSEA_ANCHOR_CREATURES_1 — build the two anchors the Grey Deep is actually about, plus the Aerofleet replacement

Ruled at the Grey Sea bedazzle sitting, 2026-09-26. Both calls are **decisions taken
by question card** — no owner quote.

## the finding that produced this

The Grey Deep's frozen sheet (`design/Jawa/worldbuilding/biomes/the_grey_deep.md` §4)
rests on **three anchor creatures**. MEASURED 2026-09-26: two of them have never
existed as defs, and the roster's own `new_defs` list still names them as owed.

| sheet anchor | status |
|---|---|
| the crusted giant | **probably built** — the roster's rename ledger maps it onto `RSW_Reefback` → "Brine Warden (adult)"; `RM_Reefback` ships. Confirm the mapping before building anything new. |
| **the pillar-mason** | **NO DEF EXISTS** |
| **the ossuary shrimp** | **NO DEF EXISTS** |

What actually ships is `RM_Reefback`, `RM_Fessk`, `RM_Sorruth`, `RM_Essarn`,
`RM_Otheska` — all real, all fine, and none of them the thing the sheet is about.

## rulings

1. **Build both missing anchors.** They are what makes the Grey Deep a place rather
   than murk with animals in it.
2. **`AA_Aerofleet` is CUT from the Grey Sea and replaced by a new creature of ours** —
   never by re-using a neighbour's, per the standing biome-specific fauna law. The cut
   is applied; the replacement is owed here.

⛔ **The cut is scoped to the Grey Sea.** `RM_TwilightSea` and `RM_TheForge` still cast
`AA_Aerofleet` deliberately. A cut in one sheet is never a planet-wide sweep — do not
"fix" the others to match.

## what each creature has to DO — from the frozen sheet, not invented

🔒 The sheet is FROZEN: **amendments add detail, they never change a ruling.** Build to
what is written.

### the pillar-mason — the Grey's monoculture
> *"a crystal-binding film that **builds** — mineral columns rising from the floor
> toward light they never reach."*

🔑 **It is a navigation system, not a creature encounter.** *"The pillars are the only
landmarks in the murk, so **all travel below is pillar-to-pillar**: waymark navigation
through blindness, this world's lane-travel pattern taken underwater. Divers carve
waymarks; a lost diver is someone who missed one pillar."*

⚠️ So this is the larger of the two by far — it implies terrain/structure generation and
a navigation affordance, not just a `PawnKindDef`. Scope it honestly before building.

### the ossuary shrimp — ⭐ the owner's own
> *"a man-sized, skeletal-seeming shrimp, moving along picking at everything it can —
> strangely intelligent and nimble, but shy and evasive."*

The undertaker racing the geology: it works the freshly dead in the narrow window before
the minerals take them. **Never caught in the open, never fights, remembers.** Solitary,
single-spawn, per the inherited bans. The sheet's "always true" line is *"The shrimp saw
you first."* — evasion AI is the deliverable, not combat stats.

### the crusted giant — confirm before building
Centuries have *"encased it in its own mineral armor — a living thing wearing the
biome's geology, indistinguishable from a drifting pillar until it moves."* It
**scrapes**, so *"fresh scrape-sign means the giant is near"*. And *"you see the
mate-mark's glow before you see anything else."*
⇒ If `RM_Reefback` is this, it may still owe the scrape-sign and glow telegraphy.

### the Aerofleet replacement
A new drifter for the Grey, ours, franchise-free. ⚠️ The sheet bans schooling in the
Grey — *"anything that schools lives in the Twilight Deep"* — and the inherited law is
**solitary everything**. So the replacement is solitary.

## before building — read, do not re-invent
🔑 This project keeps having already built the thing.
- `the_grey_deep.md` §4–§6 (§6 is HARD BANS, checkable) and `terminator_sea.md` (the
  inherited law this sheet never repeats).
- `design/Jawa/worldbuilding/biomes/rosters/the_grey_sea.json` — `new_defs` already
  describes all of these; its `fish` ruling was overturned 2026-09-26.
- `design/Jawa/worldbuilding/biomes/terminal_seas_cast_proposal_2026-09-25.md`.
- Search `src/` for each mechanism before writing C#.

## criteria
- [ ] Crusted-giant ↔ `RM_Reefback` mapping confirmed or denied in writing.
- [ ] Ossuary shrimp built: solitary, single-spawn, never fights, evasive.
- [ ] Pillar-mason scoped honestly — creature vs navigation system — before any build.
- [ ] Aerofleet replacement designed and cast, solitary, non-schooling.
- [ ] Every new def checked against §6's hard bans.
- [ ] Each gets a floor resident AND a catchable `*Catch` entry if it belongs in the
      catch, matching the `RM_Essarn` ↔ `RM_EssarnCatch` pattern already shipped.

## related
- Fish were ruled ON for the Grey Sea 2026-09-26 (owner: *"There should be fish"* /
  *"But bizarre creatures of course"*), overturning the roster's no-fish call.
- The sheet's implementation deferral (*"when the diving mods need it"*) has **expired** —
  `mandrake.rm.divinginteraction` ships.

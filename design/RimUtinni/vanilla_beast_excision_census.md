# Vanilla beast excision — census (VANILLA_BEAST_EXCISION_1, wave 1)

Owner ruling: no vanilla/DLC animal in the Utinni scenario, cut at the
scenario layer (Cherry Picker / Utinni patches), never a rename, never an
edit to vanilla defs. Full ruling and scope: `VANILLA_BEAST_EXCISION_1.md`.

This is the spec's item 1 (census) plus what it turns up about item 2/3. It
is NOT a cut — nothing in the mod set changed as a result of this pass.

## Instrument

`defs.sqlite` at `.../DefDump/defs.sqlite`, captured 2026-09-24T00:30:55Z,
`mods=623` — fingerprint checked against the live campaign mod set via
`measure coverage` (541 def types complete). Query: every `ThingDef` whose
`package_id` is one of the six official Ludeon ids
(`ludeon.rimworld[.anomaly|.biotech|.ideology|.odyssey|.royalty]`) and whose
`race` field is non-null. **308 such defs** (includes `Corpse_*` twins, mech
ThingDefs and Anomaly monsters alongside the 96 real "beast" animals — see
below for the subset that matters to biome rosters).

## Finding 1 — every wired biome roster is ALREADY vanilla-free

`src/RimUtinni/UtinniPatches/Patches/WildAnimals_*.xml` — 13 files, one per
biome that has a scenario-layer roster patch (CrackedLands→RM_FloodedCanyon,
FeverWood, Greentide, GreySea, LongShade, NightsideIce, Pyrelands, Stillsand,
TheRot, TheScald, TwilightSea, Wasteland, WeepingStones).

Comment-stripped scan (regex tag extraction inside `<Patch>`, `<!-- -->`
blocks removed first — several of these files quote the vanilla placeholder
by name IN PROSE, e.g. Pyrelands' header lists "Hare, Rat, Gazelle..." and
one inline example literally writes `<Hare>1.2</Hare>` as illustration; a
naive tag scan over the raw file would misreport both as live) against the
308-name vanilla list: **zero vanilla/DLC animal defNames in any of the 13
files' actual `<value>` blocks.**

Every one of these 13 biomes' underlying `RM_<Biome>` BiomeDef DOES carry a
vanilla-only placeholder roster at its own base (kept there on purpose so the
free-standing `RM_` mod works standalone with nothing else loaded — Q11a).
The Utinni patch either:
- **Replaces** the whole `wildAnimals` node (CrackedLands/RM_FloodedCanyon,
  Greentide, Pyrelands, Wasteland — the 4 bases that actually ship vanilla
  filler), or
- **Adds** on top of a base that already has an empty or own-cast
  `wildAnimals` block (FeverWood, LongShade, NightsideIce, TheRot — empty
  bases; GreySea, TheScald, TwilightSea, Stillsand, WeepingStones — own
  `RM_`-named cast at the base already, nothing vanilla to replace).

Checked all 15 `RM_`-prefixed BiomeDefs in the repo (the 13 above plus
`RM_GelatinousSlime` and `RM_TheChill`, neither of which has or needs a
Utinni patch — both ship their own cast at the base already) and all
30 `RUT_`-prefixed BiomeDefs (the pre-migration / not-yet-split biomes).
**No `RUT_` BiomeDef's own `wildAnimals` block names a vanilla animal
either** — where non-empty, they carry `RM_`/`RSW_`/`RUT_`/donor-mod names,
never a bare vanilla one.

⇒ **The biome-roster half of spec item 1 (`census`) finds nothing left to
cut.** Every biome's *wiring* is already ours. This is not the same as "no
vanilla beast can appear" — see Finding 2.

## Finding 2 — the vanilla ThingDefs themselves are NOT cut

`infrastructure/state/cherrypicker/CherryPicker.SHIP.xml` (the live cut
list) has **no `ThingDef/Muffalo`, `ThingDef/Warg`, `ThingDef/Toxalope`,
`ThingDef/LavaSnail`, `ThingDef/StoneCrab` or `ThingDef/ColossusToad`
entry** — grepped directly, zero hits for any of the six creatures the
owner named by example. The vanilla animal defs are alive in the mod set;
only the biome-roster *wiring* moved away from them.

Consequence: a vanilla beast can still reach a Utinni player through every
route spec item 3 names — **manhunter pulse, farm-animal wander-in,
self-tame, quest reward tables, trade caravan stock, caravan pack animal
role** — none of which read biome `wildAnimals` XML. None of these routes
has been touched this wave; they are UNMEASURED, not closed.

Also unmeasured this wave, and load-bearing before any global cut: whether
the **live world's currently-painted tiles** still use a pre-migration/
vanilla biome for any settled or reachable region. Per the standing ruling
("the planet is painted once, at the end") this is expected mid-migration
and is not evidence of anything — but it does mean a live verify session run
today would show vanilla fauna for a reason unrelated to this item (stale
tile painting), and that failure mode must not be misread as this item
failing.

## Finding 3 — the "muffalo slot" caution is partially already covered

The item's watch-out says the muffalo pack-animal slot needs an owned
replacement before muffalo can be cut. Checked `<packAnimal>true</packAnimal>`
across `src/RimMandrake`, `src/RimStarWars`, `src/RimUtinni`:

- **`RM_`-tier (franchise-free) pack animals already exist**: `RM_Tirbak` and
  `RM_Vellak`, both in `src/RimMandrake/WeepingStones/Defs/ThingDefs_Races/
  RM_WeepingStonesNatives.xml` — so the Weeping Stones biome, and any
  scenario running RM_-tier only, already has a non-vanilla pack option.
- **`RSW_`-tier (canon Star Wars) pack animals are numerous**: Bantha,
  Dewback, Eopie, Ronto, Falumpaset, Dactillion, Jamel, Fambaa, Jerba,
  Kybuck, Mudhorn, Shaak, Nerf, Runyip, Uvak, Skalder, TeeMuss, Varactyl,
  Orray — all already `packAnimal=true` in `src/RimStarWars/SWBestiary/
  Defs/ThingDefs_Races/`.

Not yet checked: whether **every biome** that currently relies on the
vanilla pack role (i.e. every biome without an owned pack animal in its own
roster) has a substitute reachable in its actual scenario configuration —
that is per-biome sitting work, not this census.

## What this wave did NOT do (deliberately)

- No Cherry Picker entry was added or removed. No def, patch or roster was
  edited.
- No non-roster route (manhunter/wander-in/self-tame/quest/trade/pack) was
  audited beyond the pack-animal existence check above.
- No live session was run to verify Finding 1's XML-level conclusion against
  a running game (the def-dump/XML read is post-load-order but pre-Cherry-
  Picker and pre-scenario; a live check is still owed before this item can
  close).

These are the concrete next steps for whoever picks this item up next; the
item itself stays open (`doing`, FOUNDRY) rather than closing, because the
`## verify` bar (a full-list live session showing zero vanilla spawns across
every route) is nowhere near met — only the biome-roster route has been
checked, and it checked clean.

## Wave 2 (2026-10-10) — the non-roster routes, measured

Instrument: `src/RimMandrake/Utils/vanilla_beast_routes.py` over `defs.sqlite` (captured 2026-10-04T17:39:06Z, full
mod list — **pre-Cherry-Picker**, so a CP cut is invisible here; the result is "what the mod set can route", not
what the Utinni scenario shows after its cuts). Selection rules are the decompiled 1.6 engine's own, read via
RimSage the same day. Sanity probe: Muffalo is found as a trader animal and a caravan carrier (OK).
115 official (Ludeon/DLC) animal pawn ThingDefs.

- **Manhunter packs** — `AggressiveAnimalIncidentUtility` draws from the map's biome rosters (`AllWildAnimals`,
  coastal and pollution lists); even its global fallback is filtered by biome commonality. ⇒ the **roster route**,
  which wave 1 found clean for `wildAnimals`. ⚠️ Not yet checked: the `coastalAnimals`/`pollutionWildAnimals` lists
  of our biomes, and Odyssey's `AnimalHabitat` tile mutator (picks its own kind, 50% manhunter chance).
- **Farm animals wander in** — engine rule: Animal, Wildness < 0.35, `AnimalFarm` trade tag, not Dryad. Official
  eligible: **10** — `Alpaca`, `Chicken`, `Cow`, `Donkey`, `Dromedary`, `Duck`, `Goat`, `Pig`, `Sheep`, `Yak`. Ours eligible: 43, so cutting
  the official ten leaves the incident live with owned animals.
- **Trader stock** — `StockGenerator_Animals`: race trade tags ∩ a trader's `tradeTagsSell`, inside its wildness
  band, tradeability can-sell. Official animals some trader can sell: **49**; ours: 642.
- **Caravan pack carriers** (`FactionDef.pawnGroupMakers[*].carriers`) — official: **6**, all from
  donor factions in the mod set:
- `Alpaca` — 24 factions (e.g. `AG_OutlanderCivilUnion`, `BS_Dvergr_Medieval_Union`, `BS_LittlePeople`)
- `Dromedary` — 23 factions (e.g. `AG_OutlanderCivilUnion`, `BS_Dvergr_Medieval_Union`, `BS_LittlePeople`)
- `Elephant` — 21 factions (e.g. `AG_OutlanderCivilUnion`, `BS_Dvergr_Medieval_Union`, `BS_LittlePeople`)
- `Horse` — 1 factions (e.g. `KAR_OrcClan`)
- `Muffalo` — 30 factions (e.g. `AG_OutlanderCivilUnion`, `BS_Dvergr_Medieval_Union`, `BS_LittlePeople`)
- `Yak` — 2 factions (e.g. `BS_Muspelheim`, `BS_Niflheim`)
  Ours already carrying for some faction: 27 kinds (Bantha, Dewback, Eopie, Ronto, …).
- **Self-tame** acts on animals already on the map ⇒ roster route. **Quest animal rewards** not measured this wave.

⇒ A Cherry Picker cut of the official animal ThingDefs should close trader stock and wander-in (both select from
`DefDatabase<PawnKindDef>`) — UNVERIFIED: confirm the cut actually removes the kind from that database rather than
zeroing a commonality, since Cherry Picker has several cut mechanisms and a commonality-0 cut does not stop either route — but the six carrier kinds are named directly by faction defs, so cutting
them without first repointing those factions' `carriers` at owned beasts breaks caravan generation for every faction
listed. That repoint is the next concrete step, faction by faction, before any CP wave touches Muffalo/Alpaca/
Dromedary/Elephant/Horse/Yak.
